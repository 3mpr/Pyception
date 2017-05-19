
from Perception.Data import *
from Perception.Data.Operators.OperatorInterface import OperatorInterface
from Perception.Data.Point import Area


class AOIOperator(OperatorInterface):

    def __init__(self, areas: list = list()) -> None:
        self.areas = areas
        self.matches = list()
        self.match_rates = list()

        i = 0
        while i < len(self.areas):
            self.matches.append(0)
            i += 1

    def visit(self, transaction: Transaction):
        if self.involve(transaction):
            print("Processing transaction with {0} AOIs.".format(len(self.areas)))
            self.match(transaction)
        return transaction

    def involve(self, transaction: Transaction):
        return "x" in transaction.headers and "y" in transaction.headers

    def when(self, transaction: Transaction, callback: callable, kwargs=None):
        if self.involve(transaction):
            callback(kwargs)

    def match(self, transaction):
        for row in transaction:
            point = Point(float(row['x']), float(row['y']))
            for area in self.areas:
                if area.contains(point):
                    self.matches[self.areas.index(area)] += 1
        self.match_rates = [self.matches[i] / transaction.count() for i in range(len(self.matches))]
