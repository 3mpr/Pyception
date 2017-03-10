# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

from GazeData import GazeData
from Point import Point

class DualEyeGazeData(GazeData):
    """
    TODO
    """

    def __init__(self, source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        super(DualEyeGazeData, self).__init__(
            str(source_file_path),
            ["Timestamp", "nouse1", "nouse2", "LeftEye", "RightEye", "GazePoint"]
        )

        self.remove_field("nouse1")
        self.remove_field("nouse2")
        self.remove_field("LeftEye")
        self.remove_field("RightEye")

        self._scale_x = scalex
        self._scale_y = scaley

        self.bootstrap_destination()

    @staticmethod
    def create(source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        return DualEyeGazeData(source_file_path, scalex, scaley, delimiter)

    def bootstrap_destination(self):
        """
        Bootstraps the basic destination csv file.
        Removes unecessary statistic rows and reformat
        malformated rows.
        """
        index = 0

        for row in self._source_csv:
            if row["LeftEye"] is not None or row["RightEye"] is not None:
                point_a = Point.create(row["LeftEye"])
                point_b = Point.create(row["RightEye"])

                if point_a is not None and point_b is not None:
                    point_a = Point.scale(point_a, self._scale_x, self._scale_y)
                    point_b = Point.scale(point_b, self._scale_x, self._scale_y)
                    self._dest_csv[index]['GazePoint'] = str(Point.center(point_a, point_b))

            else:
                del self._dest_csv[index]

            index = index + 1

    def gaze_points(self):
        for record in self._dest_csv:
            yield record['Timestamp'], record['GazePoint']

# import os
# from os.path import join
# from DualEyeGazeData import DualEyeGazeData
# edg = DualEyeGazeData(join(os.getcwd(), "Data", "Aaron.log"))