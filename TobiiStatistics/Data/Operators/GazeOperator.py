# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 27.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

from Perception.Data.Operators.GazeInterface import GazeInterface
from Perception.Data.Operators.OperatorInterface import OperatorInterface
from Perception.Data.Point import Point
from Perception.Data.Point import Area
from Perception.Data.Transaction import Transaction


class GazeOperator(OperatorInterface, GazeInterface):
    """
    This class implements logic and behaviours related to gaze coordinates.
    It detects, translates and filters raw information into analytic-ready
    data.
    """
    # ================================================ OperatorInterface

    def __init__(self, area):
        # type: (Area) -> None
        self._area = area
        self._radius_table = list()

    def visit(self, transaction):
        __doc__ = OperatorInterface.visit.__doc__
        if self.involve(transaction):
            return self.convert(transaction)
        return transaction

    def involve(self, transaction):
        __doc__ = OperatorInterface.involve.__doc__
        return "LeftEye" in transaction.headers and "RightEye" in transaction.headers

    def when(self, paper, callback, kwargs=None):
        __doc__ = OperatorInterface.when.__doc__

    # =========================================================== GazeInterface

    def focal(self, left_eye, right_eye):
        # type: (Point, Point) -> Point and float and float
        __doc__ = GazeInterface.focal.__doc__
        return Point(
            (left_eye.x + right_eye.x) / 2,
            (left_eye.y + right_eye.y) / 2
        ), abs(left_eye.x - right_eye.x), abs(left_eye.y - right_eye.y)

    def convert(self, transaction):
        # type: (Transaction) -> Transaction
        __doc__ = GazeInterface.convert.__doc__
        transaction.add("GazePoint")
        for index in range(transaction.count()):
            left_eye_point = Point.read(transaction.table[index]["LeftEye"])
            right_eye_point = Point.read(transaction.table[index]["RightEye"])

            if left_eye_point is None or right_eye_point is None:
                transaction.table[index]["GazePoint"] = ""
                continue

            left_eye_point.scale(self._area.width, self._area.height)
            right_eye_point.scale(self._area.width, self._area.height)

            focal_point, x_radius, y_radius = self.focal(left_eye_point, right_eye_point)
            self._radius_table.append({'x': x_radius, 'y': y_radius})

            transaction.table[index]["GazePoint"] = str(focal_point)
        return transaction
