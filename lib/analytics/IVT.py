# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 12.06.2017
:Status: iteral
:Copyright: MIT License
"""

import math
import statistics


class Point(object):

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance(self, b) -> float:
        dis_x = abs(self.x - b.x)
        dis_y = abs(self.y - b.y)

        return math.sqrt(pow(dis_x, 2) + pow(dis_y, 2))


class Area(object):

    def __init__(self, a: Point, b: Point) -> None:
        self.a = a
        self.b = b


class IVT(object):

    def __init__(self, threshold: float = 450.0) -> None:
        self.threshold = threshold

    def velocity(self, points: list) -> list:
        velocities = list()

        for i in range(len(points)):
            if i == 0:
                continue
            past_p = Point(float(points[i-1]["x"]), float(points[i-1]["y"]))
            cur_p = Point(points[i]["x"], points[i]["y"])
            d = cur_p.distance(past_p)
            t = abs(float(points[i]["timestamp"])
                    - float(points[i-1]["timestamp"]))
            v = d / t
            velocities.append(v)

        return velocities

    def fixation(self, points: list, velocities: list) -> list:
        if len(points) != len(velocities) + 1:
            raise Exception("Unrelated point to velocity lists."
                            +" (points: {0}, velocities: {1})").format(
                                len(points),
                                len(velocities)
                            )
        median = statistics.median(velocities)

        fixations = list()
        for i in range(len(velocities)):
            if velocities[i] < median:
                fixations.append(points[i])
