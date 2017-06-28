# -*- coding: utf-8 -*-

"""
Part of the **Pyception** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 28.06.2017
:Revision: 3
:Copyright: MIT License
"""

import os
import numpy as np
import pandas as pd
from scipy.ndimage.filters import convolve
from lib import log, Level, db_file, Repository

from .IVT import IVT
from .plan2d import matrix, circle_matrix, Point, Area


class Experiment(object):
    """
    This class encapsulates data analysis logic.

    Through the use of an algorithm (by default IVT), it can compute
    fixation matrix and heatmap for the corresponding dataset (subject /
    experience name link within database).

    A typical workfolw with this class looks as follow::

        my_subject = Subject(my_subject_name)
        my_experiment = Experiment(my_experiment_name, my_subject)
        my_experiment.analyze()
        my_experiment.make_heatmap()
        my_experiment.save()

    As such, experiments maintain a link to the Subject class which itself
    acts through similar behaviours on top of handling experiments.

    .. seealso:: Subject
    """
# ------------------------------------------------------------------- VARIABLES

    repository = Repository(db_file)
    algorithm = IVT()
    convolution_kernel = circle_matrix(80, True)
    filename = "results.xlsx"
    refresh = False

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str, subject) -> None:
        """
        Class constructor. Intializes important variables.

        :param name:    The name of the experiment.
        :param subject: The Subject that owns this experiment.
        :type name:     str
        :type subject:  Subject
        """
        self.name = name
        self.directory = os.path.join(subject.directory, name)
        self.subject = subject
        self.id = None
        self.aois = list()

        self.persistent = False
        self._load()

        self.length = None
        self.mean_frequency = None
        self.fixation_points = None
        self.fixation_matrix = None
        self.heatmap = None
        self.aois_fixations = list()

        self.analyzed = False

# --------------------------------------------------------------------- METHODS

    def _load(self) -> None:
        """
        Deferred class constructor, loads important values from the database.
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

        experiment_aois = self.repository.read({
            'experiment': self.id
        }, "experiments_aois")
        aois = list()
        for experiment_aoi in experiment_aois:
            aois.append(self.repository.read({
                'id': experiment_aoi['aoi']
            }, "aois")[0])

        for aoi_def in aois:
            self.aois.append(Area(
                Point(aoi_def["top_left_x"], aoi_def["top_left_y"]),
                Point(aoi_def["bottom_right_x"], aoi_def["bottom_right_y"])
            ))

    def _frequence_over_time(self, data: list):
        """
        Computes the frequence for each sample of the given dataset.
        Computed frequences are saved in the given list.

        :param data: List of timed coordinates.
        """
        for i, cell in enumerate(data):
            if i == 0:
                continue
            delta = cell["timestamp"] - data[i-1]["timestamp"]
            data[i]["frequence"] = 1.0 / abs(delta)

    def analyze(self) -> None:
        """
        Computes from this object variables general values such as how long
        did the experiment last, the fixation list and matrix of the gaze data
        and which (and for how long) these match the registered areas of
        interest.
        """
        log("Starting experiment analysis...")
        if not self.persistent:
            log("FATAL. Unable to analyze unpersistent experiment.",
                Level.ERROR)
            return
        if len(self.data) < 2:
            log("Inconsistent data...", linesep="")
            log(" Skipped", Level.FAILED)
            return

        log("Computing general values...", linesep="")
        self.length = abs(self.data[-1]["timestamp"]
                          - self.data[0]["timestamp"])
        self.mean_frequency = float(len(self.data)) / self.length
        self._frequence_over_time(self.data)
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
                    watch_time += fpoint["time"]
            self.aois_fixations.append({
                'aoi': str(aoi),
                'count': watch_count,
                'time': watch_time,
                'weight': watch_time / self.length * 100
            })

        self.analyzed = True
        log(" Done", Level.DONE)

    def make_heatmap(self) -> np.ndarray:
        """
        Computes through matrix convolution this experiment heatmap.
        Helpful for visualtion purpose.

        This method must be called after analyze.
        This method is computationally expensive and may take a while
        to complete.

        :return:    The computed heatmap matrix.
        :rtype:     np.ndarray
        """
        if self.heatmap:
            return self.heatmap
        if not self.analyzed:
            error_msg = "A call to analyze must be done first to the heatmap" \
                        + " construction."
            log(error_msg, Level.EXCEPTION)
            raise Exception(error_msg)

        log("Computing matrix convolution...", linesep="")
        self.heatmap = convolve(
            self.fixation_matrix,
            self.convolution_kernel
        )

        log(" Done.", Level.DONE)
        return self.heatmap

    def save(self, destination: str, refresh: bool = None) -> None:
        """
        Save this experiment analysis result to disk.
        If no path is provided, it will be built from this experiment subject
        path.

        :param destination: The destination path on disc where this experiment
                            analysis results should be saved.
        :type destination:  str
        """
        if not self.analyzed:
            log("Experiment must be analyzed prior to save.", Level.ERROR)
            return

        directory = self.directory if destination is None else destination
        refresh = self.refresh if refresh is None else refresh

        if not os.path.isdir(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, self.filename)
        if os.path.isfile(filepath) and not refresh:
            log("Experiment analytics already done, skipping.", linesep="")
            log(" Done", Level.DONE)
            return
        log("Starting experiment save...", linesep="")

        gen_data = pd.DataFrame(list({
            'id': self.id,
            'name': self.name,
            'subject': self.subject.name,
            'length': self.length,
            'mean_frequency': self.mean_frequency
        }.items()))
        writer = pd.ExcelWriter(os.path.join(directory, self.filename))
        gen_data.to_excel(writer, "general")
        for cell in self.data:
            cell["fixation"] = str(cell["fixation"])
        pd.DataFrame(self.data).to_excel(writer, "data")
        pd.DataFrame(self.fixation_points).to_excel(writer, "fixations")
        pd.DataFrame(self.aois_fixations).to_excel(writer, "aois")

        writer.save()
        log(" Done", Level.DONE)
