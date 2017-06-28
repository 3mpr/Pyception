# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 28.06.2017
:Revision: 3
:Copyright: MIT License
"""

import os
import time
import sys

import matplotlib.pyplot as plt
import pandas as pd
from overload import *

from lib import db_file, analytics_dir, log, progress, Level, Repository
from .IVT import IVT
from .Experiment import Experiment


class Subject(object):
    """
    This class is and experiments container and its **analyze** and **save**
    methods are iterative wrappers over their Experiment method counterpart.

    .. seealso:: Experiment
    """
# ------------------------------------------------------------------- VARIABLES

    db_file = db_file
    repository = Repository(db_file)

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str) -> None:
        """
        Class constructor. Intializes important variables.

        :param name:    The name of the subject.
        :type name:     str
        """
        self.name = name
        self.directory = os.path.join(analytics_dir, self.name)
        self.id = None
        self._control = None

        self._load()

        self.experiments = list()

# --------------------------------------------------------------------- METHODS

    def _load(self):
        """
        Deferred class constructor, loads important values from the database.
        """
        log("Retreiving subject %s description..." % self.name, linesep="")
        data = self.repository.read({'name': self.name}, "subjects")[0]
        if not data:
            raise Exception(
                "Subject {0} does not exist in database {1} .".format(
                    self.name, self.db_file
                )
            )
        log(" Done", Level.DONE)
        self.id = data["id"]
        self._control = data["control"] == 1

    def analyze(self) -> None:
        """
        Retreives this subject's experiments from the database before to
        loop and analyze each of those.
        """
        log("Beginning experiments analysis...", Level.INFORMATION)

        experiments = progress(
            "Retreiving %s experiments descriptions..." % self.name,
            (self.repository.read, {
                'constraints': {'subject': self.id},
                'table': "experiments"
            }), " Done"
        )

        for experiment_def in experiments:
            try:
                experiment = Experiment(experiment_def["name"], self)
                experiment.analyze()
                self.experiments.append(experiment)
            except Exception as e:
                log(e, Level.EXCEPTION)
                log("A fatal error occured. Exiting...", Level.ERROR)
                sys.exit(-1)
            except KeyboardInterrupt as ki:
                print("")
                log("Keyboard Interrupt. Exiting...", Level.INFORMATION)
                sys.exit(0)

        log("Experiments analysis completed successfully.",
            Level.INFORMATION)

    def save(self):
        """
        Save every analyzed experiments.
        """
        for experiment in self.experiments:
            experiment.save()

# ------------------------------------------------------------------ PROPERTIES
