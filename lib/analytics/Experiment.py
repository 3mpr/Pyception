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
import matplotlib
import matplotlib.pyplot as plt
from scipy.ndimage.filters import convolve

import lib as pct
from lib import Level

from .IVT import IVT
from .plan2d import matrix, circle_matrix, Point, Area


class Experiment(object):
    """
    This class encapsulates data analysis logic.

    Through the use of an algorithm (by default IVT), it can compute
    fixation matrix and heatmap for the corresponding dataset (subject /
    experience name link within database).

    A typical workflow with this class looks as follow::

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

    repository = pct.Repository(pct.SETTINGS["db_file"])
    algorithm = IVT()
    convolution_kernel = circle_matrix(80, True)
    filename = "results.xlsx"
    refresh = False
    heatmap_figure_max_value = 1.0

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str, subject) -> None:
        """
        Intializes variables to their default values.

        :param name:    The name of the experiment.
        :param subject: The Subject who owns this experiment.
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
        Deferred class constructor, loads variables values from the underlying
        repository.

        .. seealso:: Repository
        """
        pct.log("Retreiving experiment %s description..." % self.name,
                Level.DEBUG, linesep="")
        repo_self = self.repository.read({
            'name': self.name,
            'subject': self.subject.id
        }, "experiments")
        if not repo_self:
            pct.log(" Failed", Level.FAILED)
            pct.log("Experiment does not exist in database.", Level.WARNING)
            return
        repo_self = repo_self[0]
        pct.log(" Done", Level.DONE)

        self.id = repo_self['id']
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
        Operates the experiment analysis. Based on the timed coordinates
        retreived at object construction, this method calculates :

        - the experiment length ;
        - the experiment mean frequency ;
        - the frequency at each point of the dataset (the invert of the elapsed
        time between the two records) ;
        - the fixations points (through the use of a FixationDetector, IVT as
        4.07.2017)
        - the fixation matrix ;
        - the fixation / area of interest link, that is to say which fixations
        lay in which area and for how long.
        """
        pct.log("Analyzing experiment %s..." % self.id)
        if not self.persistent:
            pct.log("FATAL. Unable to analyze unpersistent experiment.",
                    Level.ERROR)
            return
        if len(self.data) < 2:
            pct.log("Inconsistent data...", Level.DEBUG, linesep="")
            pct.log(" Skipped", Level.FAILED)
            return

        pct.log("Computing general values...", Level.DEBUG, linesep="")
        self.length = abs(self.data[-1]["timestamp"]
                          - self.data[0]["timestamp"])
        self.mean_frequency = float(len(self.data)) / self.length
        self._frequence_over_time(self.data)
        pct.log(" Done", Level.DONE)

        pct.log("Computing fixations...", Level.DEBUG, linesep="")
        self.fixation_points = self.algorithm.fixation(self.data)
        pct.log(" Done", Level.DONE)
        pct.log("Computing fixation matrix...", Level.DEBUG,linesep="")
        self.fixation_matrix = matrix(self.fixation_points)
        pct.log(" Done", Level.DONE)

        pct.log("Detecting Area Of Interest matchs...", Level.DEBUG,
                linesep="")
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
        pct.log(" Done", Level.DONE)

    def make_heatmap(self) -> np.ndarray:
        """
        Computes through matrix convolution this experiment heatmap.
        Helpful for visualisation.

        This method must be called after analyze.
        This method is **computationally expensive** and may take a while to
        complete.

        :return:    The computed heatmap matrix.
        :rtype:     np.ndarray
        """
        if self.heatmap:
            return self.heatmap
        if not self.analyzed:
            error_msg = "A call to analyze must be done prior to the heatmap" \
                        + " construction."
            pct.log(error_msg, Level.EXCEPTION)
            raise Exception(error_msg)

        pct.log("Computing matrix convolution...", Level.DEBUG, linesep="")
        self.heatmap = convolve(
            self.fixation_matrix,
            self.convolution_kernel
        )

        pct.log(" Done", Level.DONE)
        return self.heatmap

    def figure(self, cmap: str = 'nipy_spectral') -> matplotlib.figure.Figure \
            and matplotlib.image and plt.colorbar:
        """
        Builds a pyplot Figure object with the previously computed heatmap in
        it. The resulting image is different from the original heatmap as
        values above **heatmap_figure_max_value** are grouped together.

        :param cmap:    The figure image color code.
        :type cmap:     str
        :return:        The composite elements of the newly created figure.
        :rtype:         plt.figure.Figure and plt.Image and plt.colorbar
        """
        if self.heatmap is None:
            pct.log("Heatmap not built yet, unable to create figure.",
                    Level.ERROR)
            return
        fig = plt.figure()
        image = plt.imshow(self.heatmap, cmap=cmap, vmin=0.0,
                           vmax=self.heatmap_figure_max_value)
        clrb = plt.colorbar()
        return fig, image, clrb

    def save(self, destination: str = None, refresh: bool = None) -> None:
        """
        Saves this experiment analysis result to disk.
        If no path is provided, the destination will be decided from this
        experiment subject path.

        :param destination: The destination path on disc where this experiment
                            analysis results should be saved.
        :type destination:  str
        :param refresh:     Whether to overwrite possibly already existing
                            experiment save or not.
        :type refresh:      bool
        """
        if not self.analyzed:
            pct.log("Experiment must be analyzed prior to save.", Level.ERROR)
            return

        directory = self.directory if destination is None else destination
        refresh = self.refresh if refresh is None else refresh

        if not os.path.isdir(directory):
            os.makedirs(directory)
        for cell in self.data:  # TODO check how to alleviate this
            cell["fixation"] = str(cell["fixation"])
        filepath = os.path.join(directory, self.filename)
        if os.path.isfile(filepath) and not refresh:
            pct.log("Experiment analytics already done, skipping.", linesep="")
            pct.log(" Done", Level.DONE)
            return
        pct.log("Starting experiment save...", linesep="")

        gen_data = pd.DataFrame(list({
            'id': self.id,
            'name': self.name,
            'subject': self.subject.name,
            'length': self.length,
            'mean_frequency': self.mean_frequency
        }.items()))

        writer = pd.ExcelWriter(os.path.join(directory, self.filename))
        gen_data.to_excel(writer, "general")
        pd.DataFrame(self.data).to_excel(writer, "data")
        pd.DataFrame(self.fixation_points).to_excel(writer, "fixations")
        pd.DataFrame(self.aois_fixations).to_excel(writer, "aois")

        writer.save()
        pct.log(" Done", Level.DONE)

# ------------------------------------------------------------------ PROPERTIES

    @property
    def saved_analysis(self):
        return os.path.isfile(os.path.join(self.directory, self.filename))
