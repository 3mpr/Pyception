# -*- coding: utf-8 -*-

# note PCI passthrough
# pci-stub.ids=10de:13c2,10de:0fbb,8086:0c01

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 28.06.2017
:Revision: 4
:Copyright: MIT License
"""

import numpy as np

from lib import log, Level, inheritdoc

from .FixationDetector import FixationDetector
from .plan2d import Point, circle_matrix


@inheritdoc
class IVT(FixationDetector):
    """
    Implementation of the **Velocity-Threshold Identification** (I-VT)
    algorithm. This algorithm separates saccades and fixations based on
    their point-to-point velocities. Considering an arbitrary threshold,
    the velocity profiles of saccadic eye movements show essentially two
    distributions: low velocities for fixations (i.e., <100 deg/sec), and
    high velocities (i.e., >300 deg/sec) for saccades.

    .. seealso:: Identifying Fixations and Saccades in Eye-Tracking
                 Protocols. Dario D. Salvucci, Joseph H. Goldberg, 2000
    """
    def __init__(self, threshold: float = 450.0, kernel_ray: int = 80) -> None:
        """
        Class constructor.

        :param threshold: The value, in pixel/s, to use to differenciate
        saccades from fixations.
        :type threshold: float
        """
        self.threshold = threshold
        log("Building {0}n ray kernel matrix...".format(str(kernel_ray)),
            Level.INFORMATION, "")
        self.kernel = circle_matrix(kernel_ray, True)

    def fixation(self, points: list) -> list:
        _ = self.speed(points)
        return self.collapse(points)

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
        for i, cell in enumerate(points):
            if i == 0:
                continue
            past_p = Point(float(points[i-1]["x"]), float(points[i-1]["y"]))
            cur_p = Point(cell["x"], cell["y"])
            dist = cur_p.distance(past_p)
            time = abs(float(cell["timestamp"])
                       - float(points[i-1]["timestamp"]))
            speed = dist / time
            points[i]["speed"] = speed
            points[i]["fixation"] = speed < self.threshold

        return points.pop(0)

    def collapse(self, points: list) -> list:
        """
        Analyzes within the given set of data the fixation status of every
        record. Consecutive fixations are grouped together in sets.
        A gravity center is then computed for each set.

        This method must be called after **speed**.

        :param points:  :param points:  A list of dictionnaries. The key/value
                        format expected is: {
                            'timestamp': float or str,
                            'x': float or str,
                            'y': float or str,
                            'speed': float,
                            'fixation': bool
                        }
        :type points:   list
        :return:        The list of gravity points
        :rtype:         list
        """
        fixation_packs = list()
        fixation_pack = list()
        in_pack = False

        for point in points:
            if point["fixation"]:
                if not in_pack:
                    if fixation_pack:
                        fixation_packs.append(fixation_pack)
                    fixation_pack = list()
                    in_pack = True
                fixation_pack.append(point)
            elif in_pack:
                if fixation_pack:
                    fixation_packs.append(fixation_pack)
                    fixation_pack = list()
                    in_pack = False
        # Ended on a fixation
        if fixation_pack:
            fixation_packs.append(fixation_pack)

        # Fixation pack collapsing
        gravity_points = list()
        for fixation_pack in fixation_packs:
            grav = Point(0.0, 0.0)
            for cell in fixation_pack:
                point = Point(cell["x"], cell["y"])
                grav += point
            grav.x /= len(fixation_pack)
            grav.y /= len(fixation_pack)
            time = abs(float(fixation_pack[-1]["timestamp"])
                       - float(fixation_pack[0]["timestamp"]))
            gravity_points.append({
                'x': grav.x,
                'y': grav.y,
                'time': time
            })

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
            base[int(point["y"]), int(point["x"])] = point["time"]
        return base
