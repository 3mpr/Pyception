# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 16.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 21.03.2017
"""


class TimeInterface(object):
    """
    Simplistic timing interface.
    """
# -------------------------------------------------------------------------------------- PROPERTIES

    @property
    def begin(self):
        """
        Returns the first timestamp of the object.
        :return: float
        """
        raise NotImplementedError("Call to interface.")

    @property
    def end(self):
        """
        Returns the last timestamp of the object.
        :return: float
        """
        raise NotImplementedError("Call to interface.")

    @property
    def time(self):
        """
        Returns how long the object data covers / lasted (in seconds).
        :return: float
        """
        raise NotImplementedError("Call to interface.")
