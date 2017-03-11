# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import re

from GazeData import GazeData
from Point import Point

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

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        return DualEyeGazeData(source_file_path, scalex, scaley, delimiter)

    def analyze_action(self, action):
        """
        TODO
        """
        begin_expr = re.compile(r"Debut{1} ([a-zA-Z]*) ([1-9]*)")
        end_expr = re.compile(r"Fin{1} ([a-zA-Z]*) ([1-9]*)")

        data = begin_expr.match(action)

    def _convert(self):
        """
        TODO
        """
        for row in self._csv:
            gaze_point = self._from_eyes_to_coord(row["LeftEye"], row["RightEye"])
            if gaze_point is not None:
                row['GazePoint'] = str(gaze_point)

    def _from_eyes_to_coord(self, left_eye, right_eye):
        """
        Takes Eyes coordinates and returns a center point.
        """
        point_a = Point.create(left_eye)
        point_b = Point.create(right_eye)
        if point_a is not None and point_b is not None:
            return Point.center(point_a, point_b)
        return None

    def gaze_points(self):
        for record in self._csv:
            yield record['Timestamp'], record['GazePoint']

    def begin(self):
        return self._csv[-1]["Timestamp"]

    def end(self):
        return self._csv[1]["Timestamp"]
        