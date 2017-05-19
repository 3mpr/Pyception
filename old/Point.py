# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the Perception package
by Florian Indot <florian.indot@gmail.com>
"""

import re

class Point(object):
    """
    Simple class that hold the 2D coordinates of a point.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, pos_x, pos_y):
        self.x = float(pos_x)
        self.y = float(pos_y)

    def __str__(self):
        return str(self.x) + ":" + str(self.y)
        
# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(point_representation):
        """
        Class factory, returns a point from a string. String format must be [x,y].
        """
        def match(expression):
            """
            Regex-match-to-point wrapper.
            """
            coord_expr = re.compile(expression)
            data = coord_expr.match(str(point_representation))

            if data is None:
                return False

            pos_x = data.group(1).replace(",", ".")
            pos_y = data.group(2).replace(",", ".")

            return Point(pos_x, pos_y)

        possible_expressions = [
            r"\[([0-9]*,[0-9]*),([0-9]*,[0-9]*)\]",
            r"([0-9]*.[0-9]*):([0-9]*.[0-9]*)"
        ]

        for expression in possible_expressions:
            point = match(expression)
            if point:
                return point

    @staticmethod
    def form(formation):
        """
        Takes a tuple (x,y) and returns a point.
        """
        return Point(formation[0], formation[1])

    @staticmethod
    def center(a, b):
        """
        Returns a point standing between the two given points.
        """
        x = (a.x + b.x)/2
        y = (a.y + b.y)/2
        return Point(x, y)

    @staticmethod
    def scale(point, scalex, scaley=None):
        """
        Scales the given point to the wanted size (in pixel).
        If no second argument is given, both coordinates are
        treated the same way.
        """
        if scaley is None:
            point.x = point.x*scalex
            point.y = point.y*scalex
        else:
            point.x = point.x*scalex
            point.y = point.y*scaley
        return point
