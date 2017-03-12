# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Updated the 12/03/2017
"""

import os
import os.path
import re

from Datasheet import Datasheet
from Point import Point
from GazeData import GazeData

class DualEyeGazeData(GazeData):
    """
    Datasheet for dual eye gaze point csv files.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, source, scalex=1920, scaley=1080, delimiter=";"):
        super(DualEyeGazeData, self).__init__(
            source,
            ["Timestamp", "ActionContext", "Action", "LeftEye", "RightEye"]
        )

        self.add("GazePoint")
        self._altered = True

        self._scale_x = scalex
        self._scale_y = scaley

        self._sequences = list()

        self._convert()

    def __iter__(self):
        return iter(self._table)

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source, scalex=1920, scaley=1080, delimiter=";"):
        return DualEyeGazeData(source, scalex, scaley, delimiter)

    def _convert(self):
        """
        TODO
        """
        for index in range(self._size):
            gaze_point = self._focal(self._table[index]["LeftEye"], self._table[index]["RightEye"])
            self._table[index]['GazePoint'] = ("" if str(gaze_point) == "None" else str(gaze_point))

    def _focal(self, left_eye, right_eye):
        """
        Takes Eyes coordinates and returns a center point.
        """
        point_a = Point.create(left_eye)
        point_b = Point.create(right_eye)
        if point_a is not None and point_b is not None:
            focal_point = Point.center(point_a, point_b)
            focal_point = Point.scale(focal_point, 1920, 1080)
            return focal_point
        return None

    def gaze_points(self):
        for record in self._table:
            yield record['Timestamp'], record['GazePoint']

    def begin(self):
        return self._table[-1]["Timestamp"]

    def end(self):
        return self._table[1]["Timestamp"]

    def raw(self):
        return self._table
