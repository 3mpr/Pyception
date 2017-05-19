# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""


class Visited(object):
    """
    VisitorInterface implementation, data-wise.
    """
    def accept(self, visitor):
        return visitor.visit(self)
