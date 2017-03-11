# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import os
import os.path
from os.path import join

from DualEyeGazeData import DualEyeGazeData
from DirectGazeData import DirectGazeData
from Point import Point
from Area import Area

class Interpret(object):
    """
    Package main class, encapsulates most of the other classes methods
    within a general "subject to data" logic.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, subject_dir, dual=True):
        self._subject_dir = subject_dir
        self._subjects = os.listdir(subject_dir)
        self._data_format = (DualEyeGazeData.create if dual else DirectGazeData.create)

# ----------------------------------------------------------------------------------------- METHODS
    def dump(self, destination_dir):
        """
        Dumps the given subject updated file in the given
        directory. If "all" is given in place of subject,
        every subjects in the subject directory will be
        dumped.
        """
        csv_ext = lambda x: str(os.path.splitext(x)[0]) + ".csv"

        for subject_file in self._subjects:
            subject_csv = self._data_format(join(self._subject_dir, subject_file))
            subject_csv.dump(os.path.join(destination_dir, csv_ext(subject_file)))

    def watched(self, subject_file, area):
        """
        TODO
        """
        subject_csv = self._data_format(join(self._subject_dir, subject_file))
        within_area = list()
        for record in subject_csv:
            point = Point.create(record["GazePoint"])
            if area.contains(point):
                within_area.append(record)
        return within_area

if __name__ == "__main__":
    print "Say something."

