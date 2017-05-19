# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 16.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 20.03.2017
"""

import re
from yaml import load


def yopen(yaml_path):
    with open(yaml_path, "r") as fin:
        data = load(fin)
    return data


class Point(object):
    """
    Simple 2D representation of a point.
    """

    REPRESENTATIONS = [re.compile(expression) for expression in [
        r"\[([0-9]*,[0-9]*),([0-9]*,[0-9]*)\]",
        r"([0-9]*.[0-9]*):([0-9]*.[0-9]*)"
    ]]

# ------------------------------------------------------------------------------------------- MAGIC

    def __init__(self, x, y):
        """
        Class constructor.
        Takes two float numbers, these respectively represent the x and y axis.
        :param x: float
        :param y: float
        """
        self.x = x
        self.y = y

        self._scale_count = 0

    def __str__(self):
        return str(self.x) + ":" + str(self.y)

# ----------------------------------------------------------------------------------------- METHODS

    @staticmethod
    def read(chain):
        """
        Point creation delegate.
        Takes a string and attemps to create a Point
        :param chain: string
        :return: Point or None on failure
        """
        for expression in Point.REPRESENTATIONS:
            point = expression.match(chain)

            if point is None:
                continue

            x = float(point.group(1).replace(",", "."))
            y = float(point.group(2).replace(",", "."))

            return Point(x, y)

    @staticmethod
    def center(a, b):
        """
        Point creation delegate.
        Takes two points an return their computed center.
        :param a: Point
        :param b: Point
        :return: Point
        """
        return Point(
            (a.x + b.x) / 2,
            (a.y + b.y) / 2
        )

    def scale(self, x_scale, y_scale=None):
        """
        Scales this point with the given value.
        The scaling value usually represents a screen resolution.
        :param x_scale: int
        :param y_scale: int
        """
        y_scale = x_scale if y_scale is None else y_scale

        self.x = self.x * x_scale
        self.y = self.y * y_scale

        self._scale_count += 1

# -------------------------------------------------------------------------------------- PROPERTIES

    @property
    def scaled(self):
        return self._scale_count


class Area(object):
    """
    Very simple 2D area representation.
    """

    def __init__(self, up_left, bottom_right):
        self.up_left = up_left
        self.bottom_right = bottom_right

        self._width = self.bottom_right.x - self.up_left.x
        self._height = self.bottom_right.y - self.up_left.y
        self._area = self._width * self._height
        self._perimeter = self._width * 2 + self._height * 2

    def __str__(self):
        return "[X:{0},Y:{1}][X:{2},Y:{3}]".format(
            str(self.up_left.x),
            str(self.up_left.y),
            str(self.bottom_right.x),
            str(self.bottom_right.y)
        )

    def contains(self, point: Point) -> bool:
        return self.up_left.x < point.x < self.bottom_right.x and self.up_left.y < point.y < self.bottom_right.y

    @property
    def area(self):
        return self._area

    @property
    def perimeter(self):
        return self._perimeter

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height