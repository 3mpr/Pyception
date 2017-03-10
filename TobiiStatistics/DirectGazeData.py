# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

from GazeData import GazeData
from Point import Point

class DirectGazeData(GazeData):
    """
    TODO
    """

    def __init__(self, source_file_path, fieldnames, delimiter=";"):
        super(DirectGazeData, self).__init__(source_file_path, fieldnames, delimiter)

    def gaze_points(self):
        raise NotImplementedError("Yet to be implemented.")

    @staticmethod
    def create(source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        raise NotImplementedError("Yet to be implemented.")

        