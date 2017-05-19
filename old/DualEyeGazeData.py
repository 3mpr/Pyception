# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the Perception package
by Florian Indot <florian.indot@gmail.com>

Last update: 13/03/2017
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
    def __init__(self, source=None, table=None, scalex=1920, scaley=1080, delimiter=";"):
        super(DualEyeGazeData, self).__init__(
            source,
            ["Timestamp", "ActionContext", "Action", "LeftEye", "RightEye"],
            table,
            delimiter=delimiter
        )

        self.add("GazePoint")
        self._altered = True

        self._scale_x = scalex
        self._scale_y = scaley

        self._sequences = list()

    def __iter__(self):
        return iter(self._table)

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source=None, table=None, scalex=1920, scaley=1080, delimiter=";"):
        return DualEyeGazeData(source, table, scalex, scaley, delimiter)

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

    def begin(self):
        return float(self._table[1]["Timestamp"].replace(",", "."))

    def end(self):
        return float(self._table[-1]["Timestamp"].replace(",", "."))

    def time(self):
        """
        Returns the time elapsed between this object first record and last record.
        """
        return self.end() - self.begin()

    def raw(self):
        return self._table
