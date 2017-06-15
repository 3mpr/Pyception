# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 13.06.2017
:Revision: 3
:Copyright: MIT License
"""

import math
import numpy as np
from pandas import DataFrame
import scipy.ndimage.filters as filters


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


class IVT(object):

    def __init__(self, threshold: float = 450.0) -> None:
        """
        Class constructor.

        :param threshold: The value, in pixel/s, to use to differenciate
        saccades from fixations.
        :type threshold: float
        """
        self.threshold = threshold
        self.mask = np.ogrid[-threshold:threshold+1, -threshold:threshold+1]

    def velocity(self, points: list) -> list:
        """
        Computes a set of velocities from the given timed coordinates
        dictionnary.

        :param points:  A list of dictionnaries. The key/value format expected
                        is: {
                            'timestamp': float or str,
                            'x': float or str,
                            'y': float or str
                        }
        :type points:   list
        :return:        The len(points) -1 list of velocities
        :rtype:         list
        """
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
        """
        Separates from the given velocities and points the fixations and
        saccades, then collapse adjacent fixation points in groups before to
        collapse those groups in gravity centers.

        :param points:      A list of dictionnaries. The key/value format expected
                            is: {
                                'timestamp': float or str,
                                'x': float or str,
                                'y': float or str
                            }
        :param velocities:  A list of velocities in pixel/s.
        :type points:       list
        :type velocities:   list
        :return:            The computed gravity centers of the found
                            fixations.
        :rtype:             list
        """
        # Guard
        if len(points) != len(velocities):
            raise Exception("Unrelated point to velocity lists."
                            + " (points: {0}, velocities: {1})".format(
                                len(points),
                                len(velocities)
                            ))

        # Fixation packs
        fixation_packs = list()
        fixation_pack = list()
        in_pack = False
        for i in range(len(velocities)):
            if velocities[i] < self.threshold:
                if not in_pack:
                    if len(fixation_pack) > 0:
                        fixation_packs.append(fixation_pack)
                    fixation_pack = list()
                    in_pack = True
                fixation_pack.append(points[i])
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
                g.x += p.x
                g.y += p.y
            g.x /= len(fixation_pack)
            g.y /= len(fixation_pack)
            t = abs(float(fixation_pack[-1]["timestamp"])
                    - float(fixation_pack[0]["timestamp"]))
            gravity_points.append({'x': g.x, 'y': g.y, 't': t})

        # End
        return gravity_points

    def matrix(self, gravities: list, max_x=1919, max_y=1079) -> np.ndarray:
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
            if float(point["x"]) > max_x or float(point["y"]) > max_y:
                continue
            base[int(point["y"]), int(point["x"])] = point["t"]
        return base

    def convolve(self, matrix: np.ndarray, size: int) -> np.ndarray:
        """
        Operate a matrix convolution with a **size** radius gradient disc
        kernel on the given **matrix** matrix.

        :param matrix:  The fixation-holder matrix.
        :param size:    The radius size in pixel of the circle.
        :type matrix:   np.ndarray
        :type size:     int
        :return:        The convolution result.
        :rtype:         np.ndarray

        .. warning::    This operation can be computationally expensive with
                        large radius.
        """
        kernel = self._circle(size)
        return filters.convolve(matrix, kernel, mode='constant')

    def _circle(self, r: int) -> np.ndarray:
        """
        Creates a gradient disc matrix with the given **r** radius.

        :param r:   The disc radius.
        :type r:    int
        :return:    The computed gradient disc matrix.
        :rtype:     np.ndarray
        """
        grd = np.arange(0., 1. + 1./r, 1./r)
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
        return retval
