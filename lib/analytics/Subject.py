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

import lib as pct
import matplotlib.pyplot as plt
import pandas as pd
import os
from lib.conf import db_file, analytics_dir

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

    def analyze(self) -> None:
        print("Retreiving {0} experiments descriptions...".format(self.name))
        experiments = self.repository.read({
                'subject': self.id
        }, "experiments")
        print("Done.")


        print("\n!! BEGINNING EXPERIMENTS ANALYSIS !!")
        analyzed_experiments = list()
        for experiment in experiments:
            print("\nRetreiving experiment {0} data.".format(
                experiment["name"])
            )
            xp_data = self.repository.read({
                'experiment': experiment["id"]
            }, "data")
            print("Done.")
            if len(xp_data) < 2:
                print("\tData is incomplete, skipping.")
                continue
            print("\tComputing general values...")
            t = abs(xp_data[-1]["timestamp"] - xp_data[0]["timestamp"])
            f = len(xp_data) / t
            ft = self.frequence_over_time(experiment["id"])
            v = self.ivt.velocity(xp_data)
            xp_data.pop(0)
            g = self.ivt.fixation(xp_data, v)
            print("\tDone.")
            print("\tComputing fixation matrix...")
            m = self.ivt.matrix(g)
            print("\tDone.")
            print("\tComputing matrix convolution...")
            r = self.ivt.convolve(m)
            print("\tDone.")

            print("\tRegistering dataset...")
            # TODO DATAFRAME
            experiment["length"] = t
            analyzed_experiments.append({
                'name': experiment["name"],
                'definition': list(experiment.items()),
                'raw': xp_data,
                'frequency_over_time': ft,
                'velocities': v,
                'gravity_points': g,
                'heatmap': r
            })
            print("\tDone.")

        print("Experiments analysis completed successfully.")
        return analyzed_experiments

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
