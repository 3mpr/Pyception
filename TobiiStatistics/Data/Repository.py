"""
Part of the <Perception> package.

created: 15.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

import csv
import os
import os.path

import yaml

from Perception.Design.Singleton import Singleton
from Perception.Subject import Subject


class Repository(object):
    """
    Handles path to Transaction/GazeData correlation.
    """

    __metaclass__ = Singleton

    def __init__(self, configuration_path):

        with open(configuration_path, "r+") as fin:
            self._conf = yaml.load(fin)

        if not os.path.exists(os.path.join(self._conf["root"], self._conf["experiments_root"])):
            os.makedirs(os.path.join(self._conf["root"], self._conf["experiments_root"]))

        self._current_experiment = None
