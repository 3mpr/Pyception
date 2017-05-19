# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 17.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 17.04.2017
"""

from overload import *

import PyQt5
from PyQt5.QtWidgets import QWidget, QGroupBox
from PyQt5.QtCore import pyqtSignal


class InteractiveQGroupBox(QGroupBox):

    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        print("constructor 1")

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
