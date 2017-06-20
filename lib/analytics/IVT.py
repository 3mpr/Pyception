# -*- coding: utf-8 -*-

# note PCI passthrough
# pci-stub.ids=10de:13c2,10de:0fbb,8086:0c01

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 16.06.2017
:Revision: 3
:Copyright: MIT License
"""

import math
import numpy as np
from pandas import DataFrame
import scipy.ndimage.filters as filters

from lib.utils import log, bold, Level


def circle_matrix(r: int, gradient: bool = False) -> np.ndarray:
    """
    Creates a disc matrix with the given **r** radius.

    :param r:   The disc radius.
    :type r:    int
    :return:    The computed gradient disc matrix.
    :rtype:     np.ndarray
    """
    log("Building {0}n ray kernel matrix...".format(str(r)),
        Level.INFORMATION, "")
    try:
        if gradient:
            grd = np.arange(0., 1. + 1./r, 1./r)
        else:
            grd = np.ones(r)
        cpt = r * 2 + 1
        retval = np.zeros((cpt, cpt))
        for i in range(cpt):
            for j in range(cpt):
                di = r + 1 - i
                dj = r + 1 - j
                delta = math.sqrt(pow(di, 2) + pow(dj, 2))
                if delta > r:
                    delta = len(grd) - 1
                retval[i-1, j-1] = 1 - grd[int(delta)]
    except Exception as e:
        log(e, Level.EXCEPTION)
        raise e
    log(" Done", Level.DONE)
    return retval


class Point(object):
    """
    Simple carthesian coordinates class.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance(self, b) -> float:
        dis_x = abs(self.x - b.x)
        dis_y = abs(self.y - b.y)

        return math.sqrt(pow(dis_x, 2) + pow(dis_y, 2))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))


class IVT(object):

    def __init__(self, threshold: float = 450.0) -> None:
        """
        Class constructor.

        :param threshold: The value, in pixel/s, to use to differenciate
        saccades from fixations.
        :type threshold: float
        """
        self.threshold = threshold
        self.kernel = circle_matrix(80, True)

    def speed(self, points: list) -> dict:
        """
        Computes the speeds and fixation from the given timed coordinates
        dictionnary. This method trim the first element of the list.

        :param points:  A list of dictionnaries. The key/value format expected
                        is: {
                            'timestamp': float or str,
                            'x': float or str,
                            'y': float or str
                        }
        :type points:   list
        :return:        The first element of the list.
        :rtype:         dict
        """
        for i in range(len(points)):
            if i == 0:
                continue
            past_p = Point(float(points[i-1]["x"]), float(points[i-1]["y"]))
            cur_p = Point(points[i]["x"], points[i]["y"])
            d = cur_p.distance(past_p)
            t = abs(float(points[i]["timestamp"])
                    - float(points[i-1]["timestamp"]))
            v = d / t
            points[i]["speed"] = v
            points[i]["fixation"] = v < self.threshold

        return points.pop(0)

    def collapse(self, points: list) -> list:
        # TODO DOC
        fixation_packs = list()
        fixation_pack = list()
        in_pack = False

        for point in points:
            if point["fixation"]:
                if not in_pack:
                    if len(fixation_pack) > 0:
                        fixation_packs.append(fixation_pack)
                    fixation_pack = list()
                    in_pack = True
                fixation_pack.append(point)
            elif in_pack:
                if len(fixation_pack) > 0:
                    fixation_packs.append(fixation_pack)
                    fixation_pack = list()
                    in_pack = False
        # Ended on a fixation
        if len(fixation_pack) > 0:
            fixation_packs.append(fixation_pack)

        # Fixation pack collapsing
        gravity_points = list()
        for fixation_pack in fixation_packs:
            g = Point(0.0, 0.0)
            for point in fixation_pack:
                p = Point(float(point["x"]), float(point["y"]))
                g += p
            g.x /= len(fixation_pack)
            g.y /= len(fixation_pack)
            weight = abs(float(fixation_pack[-1]["timestamp"])
                         - float(fixation_pack[0]["timestamp"]))
            gravity_points.append({
                'x': g.x,
                'y': g.y,
                'weight': weight
            })

        # End
        return gravity_points

    def matrix(self, gravities: list, max_x=1920, max_y=1080) -> np.ndarray:
        """
        Places the **gravities** gravity points in a newly created **max_x** *
        **max_y** matrix of zeros.

        :param gravities:   The computed gravity points as computed in
                            **self.fixation()**.
        :param max_x:       The length -1 of the x axis of the support on
                            which the data was recorded.
                            Default is set to 1919.
        :param max_y:       The length -1 of the y axis of the support on
                            which the data was recorded.
                            Default is set to 1079.
        """
        base = np.zeros((max_y, max_x))
        for point in gravities:
            if float(point["x"]) > max_x - 1 or \
               float(point["y"]) > max_y - 1:
                continue
            base[int(point["y"]), int(point["x"])] = point["weight"]
        return base

    def convolve(self, matrix: np.ndarray,
                 kernel: np.ndarray = None) -> np.ndarray:
        # TODO DOC
        """
        Operate a matrix convolution with a **size** radius gradient disc
        kernel on the given **matrix** matrix.

        :param matrix:  The fixation-holder matrix.
        :param size:    The radius size in pixel of the circle.
        :type matrix:   np.ndarray
        :return:        The convolution result.
        :rtype:         np.ndarray
        """
        kernel = self.kernel if kernel is None else kernel
        return filters.convolve(matrix, kernel, mode = 'constant')
