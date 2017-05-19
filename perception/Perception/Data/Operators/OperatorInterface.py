# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 25.03.2017
"""

from Perception.Data.Transaction import Transaction
from Perception.Design.VisitorInterface import VisitorInterface


class OperatorInterface(VisitorInterface):
    """
    This interface specifies the behaviours an Operator must implement.

    As a general rule, Operators must implements detection and operation
    mechanisms. **Operators are *meant* to be used with Transactions**.
    The former must indeed be able to detect and perform (arbitrary)
    logic on the latter.
    """
    def visit(self, transaction):
        # type: (Transaction) -> Transaction
        """
        Main Operator method, detects and operates on the given Transaction.
        visit() must **always** return a transaction. If the operator does not
        detect the wanted semantic in it, it musts return it as received.
        It can implement a communication or event system to announce whether
        the transaction has been modified or not.

        :param transaction: Transaction The operated transaction.
        :return: Transaction The (modified or not) transaction
        """
        raise NotImplementedError("Call to interface.")

    def involve(self, transaction):
        # type: (Transaction) -> bool
        """
        Detection only counterparts of **OperatorInterface.visit**.
        Returns *True* if the given transactions presents itself as
        carrying the seeked semantic, *False* otherwise

        :param transaction: Transaction The analyzed transaction.
        :return: bool
        """
        raise NotImplementedError("Call to interface.")

    def when(self, transaction, callback, kwargs=None):
        # type: (Transaction, callable, dict) -> object
        """
        Detection callback shorthand. The callback is called with the
        given dictionary parameters if the transaction carries the seeked
        semantic.

        :param transaction: Transaction The analyzed transaction
        :param callback: callable The callback
        :param kwargs: the callback parameters
        :return: object The callback return object
        """
        raise NotImplementedError("Call to interface.")
