# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a aprt of the Perception package
by Florian Indot <florian.indot@gmail.com>
"""

class Area(object):
    """
    Simplistic 2D area reprensation.
    Takes 2 points, up-left and down-right.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, point_up_left, point_down_right):
        self._up_left = point_up_left
        self._down_right = point_down_right

    def __str__(self):
        return str(self._up_left) + ";" + str(self._down_right)
# ----------------------------------------------------------------------------------------- METHODS
    def area(self):
        """
        Computes the covered area.
        """
        return (self._down_right.x - self._up_left.x) * (self._down_right.y - self._up_left.y)

    def contains(self, point):
        """
        Returns wheter the given point stands withing this area boundaries.
        """
        return(point.x >= self._up_left.x and point.x <= self._down_right.x and
               point.y >= self._up_left.y and point.y <= self._down_right.y)
