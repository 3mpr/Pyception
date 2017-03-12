#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Updated the 12/03/2017
"""

import os
import os.path
from os.path import join

from Datasheet import Datasheet
from DualEyeGazeData import DualEyeGazeData
from DirectGazeData import DirectGazeData
from Subject import Subject
from Point import Point
from Area import Area

import time

class Interpret(object):
    """
    Package main class, encapsulates most of the other classes methods
    within a general "subject to data" logic.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, subject_dir, dual=True):
        self._subject_dir = subject_dir
        self._subject_list = os.listdir(subject_dir)
        self._subjects = list()
        self._data_format = (DualEyeGazeData.create if dual else DirectGazeData.create)

        for subject in self._subject_list:
            self._subjects.append(Subject(
                self._data_format(os.path.join(self._subject_dir, subject))
            ))

# ----------------------------------------------------------------------------------------- METHODS
    def probe(self, save_path=None):
        """
        TODO
        """
        time_start = time.time()
        save_path = os.path.join(os.getcwd(), "Analytics") if save_path is None else save_path
        for subject in self._subjects:
            subject.analyze()
            subject.save(save_path)
        time_end = time.time()
        print time_end - time_start

    def watched(self, subject_file, area):
        """
        TODO
        """
        subject_csv = Datasheet(subject_file)
        within_area = subject_csv.count()
        for record in subject_csv:
            point = Point.create(record["GazePoint"])
            if point is not None:
                if not area.contains(point):
                    within_area = within_area - 1
        return float(within_area) / float(subject_csv.count())

if __name__ == "__main__":
    fin_path = join(os.getcwd(), "Analytics", "Aaron", "Foot1.csv")
    point_a = Point(1132,0)
    Point_b = Point(1920, 1080)
    area = Area(point_a, Point_b)
    itr = Interpret("RawData")
    percent = itr.watched(fin_path, area)
    print "{:2%}".format(percent)
