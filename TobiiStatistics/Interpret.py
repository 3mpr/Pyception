# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import os
import os.path
from os.path import join
import DualEyeGazeData
import DirectGazeData

class Interpret(object):
    """
    Package main class, encapsulates most of the other classes methods
    within a general "subject to data" logic.
    """
    def __init__(self, subject_dir, dual=True):
        self._subject_dir = subject_dir
        self._subjects = os.listdir(subject_dir)
        self._data_format = (DualEyeGazeData.DualEyeGazeData.create if dual
                             else DirectGazeData.DirectGazeData.create)

    def dump(self, subject_name, destination_dir):
        """
        Dumps the given subject updated file in the given
        directory. If "all" is given in place of subject,
        every subjects in the subject directory will be
        dumped.
        """
        csv_ext = lambda x: str(os.path.splitext(x)[0]) + ".csv"

        if subject_name == "all":
            for subject_file in self._subjects:
                subject_csv = self._data_format(join(self._subject_dir, subject_file))
                subject_csv.dump(os.path.join(destination_dir, csv_ext(subject_file)))
        else:
            subject_csv = self._data_format(join(self._subject_dir, subject_name))
            subject_csv.dump(os.path.join(destination_dir, csv_ext(subject_file)))


if __name__ == "__main__":
    print "Say something."
