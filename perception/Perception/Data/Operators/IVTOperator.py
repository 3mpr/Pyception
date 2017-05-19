# -*- coding: utf-8 -*-

"""
Part of the ´Perception´ package.

:Creation Date: 08-05-2017
:Author: Florian Indot ´florian.indot@gmail.com´
:Last Update: 12-05*2017
"""

from Perception.Data.Operators.GazeInterface import GazeInterface
from Perception.Data.Operators.OperatorInterface import OperatorInterface
from Perception.Data.Point import Point
from Perception.Data.Point import Area
from Perception.Data.Transaction import Transaction
from math import sqrt, pow


class IVTOperator(OperatorInterface):
    """
    Velocity-Threshold Identification algorithm implementation.

    :see: OperatorInterface
    :see: Transaction
    """
    def __init__(self, threshold: int, weight_factor: float = None) -> None:
        """
        Class constructor.

        :param threshold: The fixation speed limit between 2 points.
        :param weight_factor: The fixation size dividend factor.
        """
        self._threshold = threshold
        self._weight_factor = weight_factor

    def visit(self, transaction: Transaction) -> Transaction:
        __doc__ = OperatorInterface.visit.__doc__
        if self.involve(transaction):
            print("Processing transaction saccade to fixation with IVT algorithm.\n Threshold : {0}\n Weight Factor: {1}".format(
                self._threshold,
                "relative" if self._weight_factor is None else self._weight_factor)
            )
            return self.convert(transaction, self._weight_factor)
        return transaction

    def involve(self, transaction):
        __doc__ = OperatorInterface.involve.__doc__
        return "GazePoint" in transaction.headers

    def when(self, transaction, callback, kwargs=None):
        __doc__ = OperatorInterface.when.__doc__
        if self.involve(transaction):
            callback(kwargs)

    def velocity(self, transaction: Transaction) -> list:
        velocities = list()
        for i in range(transaction.count()):
            if i == 0:
                continue
            cp = Point.read(transaction[i]["GazePoint"])
            lp = Point.read(transaction[i-1]["GazePoint"])
            if cp is None or lp is None:
                continue
            dx = cp.x - lp.x
            dy = cp.y - lp.y
            velocities.append(sqrt(pow(dx, 2) * pow(dy, 2)))
        return velocities

    def fixation(self, transaction: Transaction, velocities: list) -> list:
        fixation_packs = list()
        fixation_pack = list()
        for i in range(len(velocities) - 1):
            if i == 0:
                continue
            # If the velocity is below the threshold, it is a fixation point
            if velocities[i] <= self._threshold:
                gravity_point = Point.read(transaction[i]["GazePoint"])
                if gravity_point is None:
                    continue
                fixation_pack.append({
                    'velocity': velocities[i],
                    'x': gravity_point.x,
                    'y': gravity_point.y,
                    'timestamp': transaction[i]["Timestamp"]
                })
                continue
            # If not and the fixationPack is empty (consecutive saccade points),
            # we move on to the next velocity.
            if len(fixation_pack) == 0:
                continue
            # If, however, it is not empty, this is the end of a fixationPack.
            # We append the fixation pack to the list of fixation packs
            # and reset the fixation pack.
            fixation_packs.append(fixation_pack)
            fixation_pack = list()
        # Might end up on a fixation pack
        if len(fixation_pack) > 0:
            fixation_packs.append(fixation_pack)
        return fixation_packs

    def convert(self, transaction: Transaction, weight_factor: float =None) -> Transaction:
        weight_factor = float(transaction.count()) if weight_factor is None else weight_factor

        velocities = self.velocity(transaction)
        fixation_packs = self.fixation(transaction, velocities)
        fixations = Transaction([], ['start', 'weight', 'x', 'y'])

        for fixation_pack in fixation_packs:

            weight = float(len(fixation_pack)) / weight_factor
            start = fixation_pack[0]["timestamp"]
            x = 0.0
            y = 0.0

            for fixation_point in fixation_pack:
                x += float(fixation_point['x'])
                y += float(fixation_point['y'])

            gravitation_point = Point(
                x / float(len(fixation_pack)),
                y / float(len(fixation_pack))
            )

            fixations.append({
                'start': start,
                'weight': weight,
                'x': gravitation_point.x,
                'y': gravitation_point.y
            })

        return fixations
