# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 21.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 22.03.2017
"""

import re

from Perception.Data.Transaction import Transaction
from Perception.Data.Operators.ChunkInterface import ChunkInterface
from Perception.Data.Operators.OperatorInterface import OperatorInterface


class ChunkOperator(OperatorInterface, ChunkInterface):
    """
    Simple implementation of the OperatorInterface, aimed at
    detecting and dividing chunks in a given Transaction.

    The division operate only if the headers "Action" and
    "ActionArgs" are available in the Transaction.
    """

    START_EXPRESSION = re.compile(r'Debut ([a-zA-Z\s]*) ([1-9]*)')
    END_EXPRESSION = re.compile(r'Fin ([a-zA-Z\s]*) ([1-9]*)')

    # ================================================ OperatorInterface

    def __init__(self, to_visit=None):
        self._chunks = {}
        self._visited = None
        if to_visit is not None:
            self.visit(to_visit)

    def visit(self, transaction):
        # type: (Transaction) -> bool or list or dict
        __doc__ = OperatorInterface.visit.__doc__
        """
        As ChunkOperator attempts to detect transaction division, this
        method always return the given paper as backward Operator compatibility.
        For proper chunk access, refer to the **chunks** property after the
        transaction visit.
        """
        if self.involve(transaction):
            self._chunks = self.divide(transaction)
        return transaction

    def involve(self, transaction):
        # type: (Transaction) -> bool
        __doc__ = OperatorInterface.involve.__doc__
        transaction = self._visited if transaction is None else transaction
        if "Action" not in transaction.headers or "ActionArgs" not in transaction.headers:
            return False
        triggers = transaction.occurrence("Trigger", "Action")
        if len(triggers) is 0:
            return False
        return True

    def when(self, transaction, callback, kwargs=None):
        # type: (Transaction, callable, dict) -> bool
        __doc__ = OperatorInterface.when.__doc__
        kwargs = {} if kwargs is None else kwargs
        if self.involve(transaction):
            callback(**kwargs)
            return True
        return False

    # ========================================================== ChunkInterface

    def divide(self, transaction):
        # type: (Transaction) -> dict
        __doc__ = ChunkInterface.divide.__doc__

        chunks = {}
        chunks_details = list()
        in_chunk = False
        triggers = transaction.occurrence("Trigger", "Action")

        for trigger in triggers:
            action = transaction.table[trigger]["ActionArgs"]
            if not in_chunk:

                begin = ChunkOperator.START_EXPRESSION.match(action)
                if not begin:
                    raise AssertionError("Expected start sequence, got {}.".format(action))
                name = begin.group(1) + begin.group(2)
                chunks_details.append({"name": name, "start": trigger})
                in_chunk = True

            else:

                end = ChunkOperator.END_EXPRESSION.match(action)
                if not end:
                    raise AssertionError("Expected end sequence, got {}.".format(action))
                chunks_details[len(chunks_details) - 1]["end"] = trigger
                in_chunk = False

        headers = transaction.headers
        headers.remove("Action")
        headers.remove("ActionArgs")

        for chunk_specification in chunks_details:
            chunks[chunk_specification["name"]] = transaction.copy(
                chunk_specification["start"],
                chunk_specification["end"],
                headers
            )

        return chunks

    @property
    def chunks(self):
        return self._chunks
