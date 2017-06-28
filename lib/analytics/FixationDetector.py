# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 28.06.2017
:Revision: 1
:Copyright: MIT License
"""

from abc import ABCMeta


class FixationDetector(metaclass=ABCMeta):
    """
    Abstract class intented to be inherited by any class which purpose would be
    to translate gaze data into fixation data.
    """
    def fixation(self, points: list) -> list:
        """
        Transalates timed cartesian coordinates into fixations.

        :param points:  The timed cartesian coordinates list.
        :type points:   list
        """
        raise NotImplementedError("Call to abstract class.")
