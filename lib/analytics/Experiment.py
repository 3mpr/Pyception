# -*- coding: utf-8 -*-

"""
Part of the **Pyception** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 25.06.2017
:Revision: 3
:Copyright: MIT License
"""

from scipy.ndimage.filters import convolve
from lib import log, Level, db_file, Repository

from .IVT import IVT
from .plan2d import matrix, circle_matrix, Point, Area


class Experiment(object):
    """
    TODO
    """
# ------------------------------------------------------------------- VARIABLES

    repository = Repository(db_file)
    algorithm = IVT()
    convolution_kernel = circle_matrix(80, True)

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name, subject):
        self.name = name
        self.subject = subject
        self.id = None
        self.aois = list()

        self.persistent = False
        self._load()

        self.length = None
        self.mean_frequency = None
        self.tfr = None
        self.fixation_points = None
        self.fixation_matrix = None
        self.heatmap = None
        self.aois_fixations = list()

# --------------------------------------------------------------------- METHODS

    def _load(self) -> None:
        """
        TODO
        """
        log("Retreiving experiment %s description..." % self.name, linesep="")
        this = self.repository.read({
            'name': self.name,
            'subject': self.subject.id
        }, "experiments")
        if not this:
            log(" Failed", Level.FAILED)
            log("Experiment does not exist in database.", Level.WARNING)
            return
        this = this[0]
        log(" Done", Level.DONE)
        self.id = this['id']
        self.data = self.repository.read({'experiment': self.id}, "data")
        self.persistent = True

        experiment_aois = self.repository.read({'experiment': self.id}, "experiments_aois")
        aois = list()
        for experiment_aoi in experiment_aois:
            aois.append(self.repository.read({'id': experiment_aoi['aoi']}, "aois")[0])

        for aoi_def in aois:
            self.aois.append(Area(
                Point(aoi_def["top_left_x"], aoi_def["top_left_y"]),
                Point(aoi_def["bottom_right_x"], aoi_def["bottom_right_y"])
            ))

    def _frequence_over_time(self, data):
        """
        TODO
        """
        tfr = list()
        for i, cell in enumerate(data):
            if i == 0:
                continue
            delta = cell["timestamp"] - data[i-1]["timestamp"]
            tfr.append(1.0 / abs(delta))
        return tfr

    def analyze(self):
        """
        TODO
        """
        log("Starting experiment analysis...")
        if not self.persistent:
            log("FATAL. Unable to analyze unpersistent experiment.",
                Level.ERROR)
            return

        log("Computing general values...", linesep="")
        self.length = abs(self.data[-1]["timestamp"]
                          - self.data[0]["timestamp"])
        self.mean_frequency = float(len(self.data)) / self.length
        self.tfr = self._frequence_over_time(self.data)
        log(" Done", Level.DONE)

        log("Computing fixations...", linesep="")
        self.fixation_points = self.algorithm.fixation(self.data)
        log(" Done", Level.DONE)
        log("Computing fixation matrix...", linesep="")
        self.fixation_matrix = matrix(self.fixation_points)
        log(" Done", Level.DONE)

        log("Detecting Area Of Interest matchs...", linesep="")
        for aoi in self.aois:
            watch_count = 0
            watch_time = 0.0
            for fpoint in self.fixation_points:
                if aoi.contains(Point(fpoint["x"], fpoint["y"])):
                    watch_count += 1
                    watch_time += fpoint["weight"]
            self.aois_fixations.append({
                'aoi': str(aoi),
                'count': watch_count,
                'time': watch_time
            })
        log(" Done", Level.DONE)

    def make_heatmap(self):
        if not self.heatmap:
            log("Computing matrix convolution...", linesep="")
            self.heatmap = convolve(self.fixation_matrix, self.convolution_kernel)
            log(" Done.", Level.DONE)
        return self.heatmap

    def save(self):
        """
        TODO
        """
        pass
