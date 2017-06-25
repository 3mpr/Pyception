# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 25.06.2017
:Revision: 1
:Copyright: MIT License
"""

from abc import ABCMeta


class FixationDetector(metaclass=ABCMeta):

    def fixation(self, points: list) -> list:
        """
        TODO
        """
        raise NotImplementedError("Call to abstract class.")
