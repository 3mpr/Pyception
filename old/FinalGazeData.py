# -*- coding: utf-8 -*-

"""
Written the 13/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

from GazeData import GazeData
from Point import Point
from Area import Area

class FinalGazeData(GazeData):
    """
    Simplistic representation of Gaze Data.
    This object holds a table of 2 elements,
    Timestamp and GazeData
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, source=None, table=None, scalex=1920, scaley=1080, delimiter=";"):
        super(FinalGazeData, self).__init__(
            source,
            ["Timestamp", "GazePoint"],
            table,
            delimiter=delimiter
        )

    def __iter__(self):
        return iter(self._table)

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source=None, table=None, scalex=1920, scaley=1080, delimiter=";"):
        return FinalGazeData(source, table, scalex, scaley, delimiter)

    def begin(self):
        return float(self._table[1]["Timestamp"].replace(",", "."))

    def end(self):
        return float(self._table[-1]["Timestamp"].replace(",", "."))

    def time(self):
        return self.end() - self.begin()

    def watch(self, area):
        """
        TODO
        """
        watch_rate = self.size()
        for record in self._table:
            gaze_point = Point.create(record["GazePoint"])
            if gaze_point is None or not area.contains(gaze_point):
                watch_rate = watch_rate -1

        return (float(watch_rate) / float(self.size())), watch_rate
        