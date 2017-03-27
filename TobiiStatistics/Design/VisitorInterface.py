# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 25.03.2017
"""


class VisitorInterface(object):
    """
    Objects implementing this interface must act according to
    the **visitor pattern**.

    The main purpose of this interface (in this project) is to
    separate data and data behaviour. Transactions are, as of
    25.03.2017, the only aimed class
    """
    def visit(self, obj):
        """
        Implements an arbitrary logic in the given object.

        :param obj: The visited object (must implement visited)
        :return: obj
        """
        raise NotImplementedError("Call to interface.")
