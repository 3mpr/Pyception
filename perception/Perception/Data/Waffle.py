from Perception.Data.Operators import *
from Perception.Data import *


class TransactionContext(object):
    """
    This class holds information relative to a ´Transaction´ details.
    The information stored is not necessary to Transaction logic and actions in itself.
    As such it is intended to provide the necessary details to act upon
    or extend the abilities of a given ´Transaction´.

    :see: Transaction
    :see: OperatorInterface
    :see: Subject
    """

    GazeOp = GazeOperator(Area(Point(0,0), Point(1920, 1080)))
    ChunkOp = ChunkOperator()
    TimeOp = TimeOperator()
    IVTOp = IVTOperator(200)
    AOIOp = AOIOperator()

    def __str__(self, transaction: Transaction, subject: Subject, experiment: str, atlas: dict = None) -> None:
        """
        Class constructor.

        :param transaction: str The transaction
        :param subject: str The transaction subject
        :param experiment: str The transaction experiment
        :param atlas: dict key-value store, will be analyzed and expanded for Operators creation
        :return:
        """
        self.transaction = transaction
        self.subject = subject
        self.experiment = experiment

        self.operators = []
        self.atlas = {} if atlas is None else atlas
        self.expand(self.atlas)

    @staticmethod
    def expand(atlas: dict) -> None:
        """
        TODO
        :param atlas:
        """
        # IVT
        ivtop_args = {}
        if "ivt:weight" in atlas.keys():
            ivtop_args["weight_factor"] = atlas["ivt:weight"]
        if "ivt:threshold" in atlas.keys():
            ivtop_args["threshold"] = atlas["ivt:threshold"]
        else:
            ivtop_args["threshold"] = 200
        TransactionContext.IVTOp = IVTOperator(**ivtop_args)

        # (...) others (...)

    def register(self, operator: OperatorInterface) -> None:
        """
        Add an operator to this object operator list.
        :param operator: ´OperatorInterface´ The Operator
        """
        if operator not in self.operators:
            self.operators.append(operator)

    def pull(self) -> None:
        """
        Raise the internal transaction to analysis level.
        """
        self.subject.raw = self.transaction
        self.subject.raw = self.GazeOp.visit(self.transaction)

        self.ChunkOp.visit(self.transaction)
        self.subject.blocks.update(self.ChunkOp.chunks)

        self.TimeOp.visit(self.subject.raw)
        self.IVTOp.visit(self.subject.raw)
        self.AOIOp.visit(self.subject.raw)

        for block in self.subject.blocks:
            self.TimeOp.visit(self.subject.blocks[block])
            self.IVTOp.visit(self.subject.blocks[block])
            self.AOIOp.visit(self.subject.blocks[block])
