# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 16.06.2017
:Revision: 3
:Copyright: MIT License
"""

import os
import time

import lib as pct
from lib.utils import log, progress, Level, bold
from lib.conf import db_file, analytics_dir

import matplotlib.pyplot as plt
import pandas as pd
from overload import *


class Subject(object):

# ------------------------------------------------------------------- VARIABLES

    db_file = db_file
    repository = pct.Repository(db_file)
    analytics_folder = analytics_dir
    ivt = pct.IVT()

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, name: str) -> None:
        self.name = name
        data = self.repository.read({'name': name}, "subjects")[0]
        if len(data) == 0:
            raise Exception(
                "Subject {0} does not exist in database {1} .".format(
                    name, self.db_file
                )
            )
        self.id = data["id"]
        self._control = data["control"] == 1

# --------------------------------------------------------------------- METHODS

    @overload
    def analyze(self) -> list:
        log(bold("Beginning experiments analysis..."), Level.INFORMATION)

        experiments = progress(
            "Retreiving %s experiments descriptions..." % bold(self.name),
            (self.repository.read, {
                'constraints': {'subject': self.id},
                'table': "experiments"
            }), " Done."
        )

        analyzed_experiments = list()
        for xp in experiments:
            res = self.analyze(xp)
            if res is not None:
                analyzed_experiments.append(res)

        log("Experiments analysis completed successfully.", Level.INFORMATION)
        return analyzed_experiments

    @analyze.add
    def analyze(self, experiment: dict) -> dict:
        try:
            start_t = time.time()

            xp_data = progress(
                "Retreiving experiment %s data..." % bold(experiment["name"]),
                (self.repository.read, {
                    'constraints': {'experiment': experiment["id"]},
                    'table': "data"
                }), " Done."
            )

            if len(xp_data) < 2:
                log("Inconsistent data, skipping.", Level.WARNING)
                return

            log("Computing general values...", Level.INFORMATION, "")
            t = abs(xp_data[-1]["timestamp"] - xp_data[0]["timestamp"])
            ft = self.frequence_over_time(experiment["id"])
            _ = self.ivt.speed(xp_data)
            g = self.ivt.collapse(xp_data)
            log(" Done.", Level.DONE)

            log("Computing fixation matrix...", Level.INFORMATION, "")
            m = self.ivt.matrix(g)
            log(" Done.", Level.DONE)

            log("Computing matrix convolution...", Level.INFORMATION, "")
            r = self.ivt.convolve(m)
            log(" Done.", Level.DONE)

            log("Registering dataset...", Level.INFORMATION, "")
            # TODO DATAFRAME
            experiment["length"] = t
            xp = {
                'name': experiment["name"],
                'definition': list(experiment.items()),
                'raw_data': xp_data,
                'frequency_over_time': ft,
                'gravity_points': g,
                'heatmap': r
            }
            log(" Done ({0:.2f}s).".format(time.time() - start_t), Level.DONE)

            return xp

        except Exception as e:
            log(e, Level.EXCEPTION)
            raise e

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
            workbook = writer.book
            keys = ["definition", "raw", "frequency_over_time",
                    "gravity_points", "velocities"]
            for key in keys:
                pd.DataFrame(result[key]).to_excel(writer, key)
            writer.save()

            plt.imsave(os.path.join(xp_dir, "heatmap.png"), result["heatmap"])
        print("Done.")

    def frequence_over_time(self, experiment: int) -> list:
        data = self.repository.read({'experiment': experiment}, "data")

        ft = list()
        for i in range(len(data)):
            if i == 0:
                continue
            ft.append({
                'time': float(data[i]["timestamp"]),
                'frequence': abs(1.0 / (float(data[i]["timestamp"])
                                        - float(data[i-1]["timestamp"])))
            })

        return ft

# ------------------------------------------------------------------ PROPERTIES
