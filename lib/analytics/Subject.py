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
import sys

import matplotlib.pyplot as plt

import lib as pct
from lib import SETTINGS, Level, Repository
from .Experiment import Experiment


class Subject(object):
    """
    This class is an experiments container. Its **analyze** and **save**
    methods are iterative wrappers over their Experiment method counterpart.

    .. seealso:: Experiment
    """
# ------------------------------------------------------------------- VARIABLES

    db_file = SETTINGS["db_file"]
    repository = Repository(db_file)

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str, repo: Repository = None) -> None:
        """
        Class constructor. Intializes important variables.

        :param name:    The name of the subject.
        :type name:     str
        """
        self.name = name
        self.directory = os.path.join(SETTINGS["analytics_dir"], self.name)
        self.id = None
        self._control = None

        self.repository = self.repository if repo is None else repo
        self._load()

        self.experiments = list()
        self.pull()

# --------------------------------------------------------------------- METHODS

    def _load(self):
        """
        Deferred class constructor, loads important values from the database.
        """
        pct.log("Retreiving subject %s description..." % self.name,
                Level.DEBUG, linesep="")
        data = self.repository.read({'name': self.name}, "subjects")[0]
        if not data:
            pct.log(" Failed", Level.FAILED)
            pct.log("Subject does not exist in database.", Level.WARNING)
            return
        pct.log(" Done", Level.DONE)
        self.id = data["id"]
        self._control = data["control"] == 1

    def pull(self) -> None:
        '''
        TODO
        '''
        pct.log("Retreiving %s experiments descriptions..." % self.name,
                Level.DEBUG, linesep="")
        experiments = self.repository.read({'subject': self.id}, "experiments")
        pct.log(" Done", Level.DONE)
        for experiment in experiments:
            self.experiments.append(Experiment(experiment["name"], self))

    def analyze(self, draw_heatmap: bool = False) -> None:
        """
        TODO REMAKE
        Retreives this subject's experiments from the database before to
        loop and analyze each of those.
        """
        pct.log("Beginning subject {0} experiments analysis...".format(
            self.id
        ), Level.INFORMATION)

        if not self.experiments:
            self.pull()
        for experiment in self.experiments:
            try:
                experiment.analyze()
                if draw_heatmap and experiment.analyzed:
                    experiment.make_heatmap()
            except Exception as e:
                pct.log(e, Level.EXCEPTION)
                pct.log("A fatal error occured. Exiting...", Level.ERROR)
                sys.exit(-1)
            except KeyboardInterrupt as ki:
                print("")
                pct.log("Keyboard Interrupt. Exiting...", Level.INFORMATION)
                sys.exit(0)

        pct.log("Experiments analysis completed successfully.",
                Level.INFORMATION)

    def save(self):
        """
        Save every analyzed experiments.
        """
        for experiment in self.experiments:
            experiment.save()
            if experiment.heatmap is not None:
                plt.imsave(
                    os.path.join(experiment.directory, "heatmap.png"),
                    experiment.heatmap,
                    cmap='nipy_spectral'
                )

                fig, img, clrb = experiment.figure()
                fig.savefig(
                    os.path.join(experiment.directory, "heatmap_figure.png")
                )
                fig.clear()

# ------------------------------------------------------------------ PROPERTIES

    @property
    def saved_analysis(self):
        sa = True
        for experiment in self.experiments:
            sa = sa and experiment.saved_analysis
        return sa
