# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 06.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 17.04.2017
"""

import PyQt5
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class InteractiveQLabel(QLabel):

    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def __init__(self, text, parent):
        super().__init__(text, parent)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
