# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 22.06.2017
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

# ------------------------------------------------------------------- VARIABLES

    db_file = db_file
    repository = Repository(db_file)
    analytics_folder = analytics_dir

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str) -> None:
        """
        Class constructor.

        TODO
        """
        self.name = name
        self.id = None
        self._control = None

        self._load()

        self.experiments = list()

# --------------------------------------------------------------------- METHODS

    def _load(self):
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

    def analyze_and_save(self):
        results = self.analyze()
        root_dir = os.path.join(self.analytics_folder, self.name)
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)
        print("\nSaving...")
        for result in results:
            xp_dir = os.path.join(root_dir, result["name"])
            if not os.path.exists(xp_dir):
                os.makedirs(xp_dir)

            writer = pd.ExcelWriter(os.path.join(xp_dir, "resume.xlsx"))
            keys = ["definition", "raw", "frequency_over_time",
                    "gravity_points", "velocities"]
            for key in keys:
                pd.DataFrame(result[key]).to_excel(writer, key)
            writer.save()

            plt.imsave(os.path.join(xp_dir, "heatmap.png"), result["heatmap"])
        print("Done")

# ------------------------------------------------------------------ PROPERTIES
