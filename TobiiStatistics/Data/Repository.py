"""
Part of the <Perception> package.

created: 15.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

import csv
import os
import os.path
import collections

import yaml

from Perception.Design.Singleton import Singleton
from Transaction import Transaction

from Operators.ChunkOperator import ChunkOperator
from Operators.GazeOperator import GazeOperator
from Point import Point, Area

class Repository(object):
    """
    Handles path to Transaction/GazeData correlation.
    """

    __metaclass__ = Singleton

    def __init__(self):
        self.FILE2TRANSACTION = {
            "log": Repository._open_log,
            "csv": Repository._open_csv,
            "json": Repository._open_json
        }

    def open(self, file_path, kwargs=None):
        kwargs = {} if kwargs is None else kwargs

        file_name = os.path.basename(file_path)
        file_extension = file_name.split(".")[1]

        if file_extension in self.FILE2TRANSACTION:
            return self.FILE2TRANSACTION[file_extension](file_path, **kwargs)

        raise NotImplementedError("Repository cannot open {} files".format(file_extension))

    def export(self, file_path, destination_directory, kwargs=None):
        file_directory = os.path.basename(file_path).split(".")[0]
        print file_directory
        target_directory = os.path.join(destination_directory, file_directory)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        transaction = self.open(file_path, kwargs)
        transaction.save(os.path.join(target_directory, "raw.csv"))

        chunk_operator = ChunkOperator()
        gaze_operator = GazeOperator(Area(Point(0, 0), Point(1920, 1080)))

        transaction / chunk_operator

        chunks = dict()

        for chunk_name in chunk_operator.chunks:
            chunks[chunk_name] = chunk_operator.chunks[chunk_name] / gaze_operator
            chunks[chunk_name].save(os.path.join(target_directory, chunk_name + ".csv"))


    @staticmethod
    def _open_log(file_path, **kwargs):
        return Transaction.open(file_path, **kwargs)

    @staticmethod
    def _open_csv(file_path, kwargs):
        raise NotImplementedError("CSV Format not implemented yet.")

    @staticmethod
    def _open_json(file_path, kwargs):
        raise NotImplementedError("JSON Format not implemented yet.")