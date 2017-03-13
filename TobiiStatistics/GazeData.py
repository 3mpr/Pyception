# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Last update: 13/03/2017
"""

from Datasheet import Datasheet
from Point import Point

class GazeData(Datasheet):
    """
    Abstract class that implements a single generator for gazing data.
    Implementing classes must implement this method in order to give correct
    gaze data. That is to say a Timestamp and Point per iteration.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __iter__(self):
        raise NotImplementedError("Call to abstract class.")

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source, table=None, scalex=1920, scaley=1080, delimiter=";"):
        """
        Tiny factory to delegate object creation.
        """
        raise NotImplementedError("Call to abstract class.")

    def begin(self):
        """
        Returns the first timestamp.
        """
        raise NotImplementedError("Call to abstract class.")

    def end(self):
        """
        Returns the last timestamp.
        """
        raise NotImplementedError("Call to abstract class.")

    def time(self):
        """
        Returns the time elapsed between the first record an
        the last record of this dataset.
        """
        raise NotImplementedError("Call to abstract class.")
