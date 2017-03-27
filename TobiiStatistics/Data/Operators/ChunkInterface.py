# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""


class ChunkInterface(object):
    """
    This interface enumerates the methods a class intending to find
    data division within a Transaction should provide.
    """
# -------------------------------------------------------------------------------------- PROPERTIES

    def divide(self, obj):
        """
        Divides a single Transaction in a list of Transaction.

        :type obj: Transaction
        :return: list(Transaction)
        """
        raise NotImplementedError("Call to interface.")
