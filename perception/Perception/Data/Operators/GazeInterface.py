# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created:** 24.03.2017
| **author:** Florian Indot <florian.indot@gmail.com>
| **last updated:** 27.03.2017
"""


class GazeInterface(object):
    """
    This interface specifies the actions an object must be
    able to perform in order to be used as an eye-tracking
    data container.
    """

    def focal(self, left_eye, right_eye):
        """
        This method must return the point of attention of a
        transaction row. This might imply a simple copy paste
        as it might imply a more elaborated calculation.
        """
        raise NotImplementedError("Call to interface.")

    def convert(self, transaction):
        """
        Converts a given transaction from a given (single / dual)
        data format to a uni focalization point format.
        """
        raise NotImplementedError("Call to interface.")