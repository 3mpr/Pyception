# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 20.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

import blessed
import collections
import array

RenderBlock = collections.namedtuple('RenderBlock', ('height', 'width', 'margin'))
Point = collections.namedtuple('Point', ('x', 'y'))

class Screen(object):

    def __init__(self):
        self.TERM = blessed.Terminal()
        self._position = Point(x=0, y=0)
        self._elements = list()
        self._matrix = array.array('u')







