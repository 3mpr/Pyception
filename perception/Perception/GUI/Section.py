# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 03.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 14.04.2017
"""

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

class Section(object):
    """
    Represents a section of the Category object.
    """
    def __init__(self, file_path: str, name: str) -> None:
        self.name = name
        self.file_path = file_path

        self.widget = None
        self.loaded = False

    def load(self):
        """
        Builds the qml file found at <self._file_path> in <self._widget>.
        """
        self.widget = uic.loadUi(self.file_path)
        if self.widget is None:
            raise IOError("Unable to load {}.".format(self.file_path))
        self.loaded = True

    @staticmethod
    def cast(obj):
        raise NotImplementedError("Call to abstract method.")

    def find(self, widget: type, name: str) -> QWidget:
        return self.widget.findChild(widget, name)
