# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

from Perception.Data.Operators.OperatorInterface import OperatorInterface
from Perception.Data.Operators.TimeInterface import TimeInterface


class TimeOperator(OperatorInterface, TimeInterface):
    """
    Simple implementation of the OperatorInterface, aimed at
    detecting whether the visited Transaction maintains Timestamps or not.

    If it does, the *TimeOperator* implements the *TimeInterface* as well,
    making it able to retrieve and compute the elapsed time of the
    visited transaction. Although the way to retrieve the time is rather
    basic and aimed at a specific layout, other implementations
    might be necessary for alternative Transaction layouts.
    """

    # ================================================ OperatorInterface

    def __init__(self, to_visit=None, skip_first_timestamp=True):
        self.skip_first_timestamp = skip_first_timestamp
        self._visited = None
        if to_visit is not None:
            self.visit(to_visit)

    def visit(self, paper):
        __doc__ = OperatorInterface.visit.__doc__
        if "Timestamp" in paper.headers:
            self._visited = paper
        else:
            self._visited = None
        return paper

    def involve(self, paper=None):
        __doc__ = OperatorInterface.involve.__doc__
        obj = self._visited if paper is None else paper
        if "Timestamp" in obj.headers:
            return True
        return False

    def when(self, paper, callback, kwargs=None):
        __doc__ = OperatorInterface.when.__doc__
        kwargs = {} if kwargs is None else kwargs
        if self.involve(paper):
            callback(**kwargs)
            return True
        return False

    # =========================================================== TimeInterface

    @property
    def begin(self):
        __doc__ = TimeInterface.begin.__doc__
        if self.involve(self._visited):
            if self.skip_first_timestamp:
                return float(self._visited.table[1]["Timestamp"].replace(',', '.'))
            else:
                return float(self._visited.table[0]["Timestamp"].replace(',', '.'))
        return -1.0

    @property
    def end(self):
        __doc__ = TimeInterface.end.__doc__
        if self.involve(self._visited):
            return float(self._visited.table[-1]["Timestamp"].replace(',', '.'))
        return -1.0

    @property
    def time(self):
        __doc__ = TimeInterface.time.__doc__
        if self.involve(self._visited):
            return self.end - self.begin
        return -1.0
