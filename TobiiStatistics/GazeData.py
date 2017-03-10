# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

from Datasheet import Datasheet
from Point import Point

class GazeData(Datasheet):
    """
    Abstract class that implements a single generator for gazing data.
    Implementing classes must implement this method in order to give correct
    gaze data. That is to say a Timestamp and Point per iteration.
    """

    def gaze_points(self):
        """
        This method is a generator that returns a Point and a timestamp per iteration.
        """
        raise NotImplementedError("Object GazeData should not be instanciated in itself!")

    @staticmethod
    def create(source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        """
        Tiny factory to delegate object creation.
        """
        raise NotImplementedError("Object GazeData should not be instanciated in itself!")
