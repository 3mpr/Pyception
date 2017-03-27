# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 16.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

import re


class Subject(object):
    """
    TODO
    """

# ------------------------------------------------------------------------------------------- MAGIC

    def __init__(self, name, data):
        self._name = name
        self._data = data

# ----------------------------------------------------------------------------------------- METHODS

# -------------------------------------------------------------------------------------- PROPERTIES

    @property
    def name(self, name=None):
        if name is None:
            return self._name
        else:
            self._name = name