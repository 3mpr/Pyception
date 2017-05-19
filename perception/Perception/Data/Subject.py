from Perception.Data.Transaction import Transaction


class Subject(object):

    def __init__(self, transaction: Transaction or list) -> None:
        self.raw = None
        self.blocks = {}
        if transaction is Transaction:
            self.raw = transaction
        elif transaction is list:
            self.blocks.extend(transaction)
