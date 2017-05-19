# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 03.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 08.04.2017
"""

import os

from PyQt5.QtWidgets import QWidget, QGroupBox, QStackedWidget, QLabel, QListWidget

from .Section import Section


class SectionHome(Section):

    def __init__(self, widget, index):
        super().__init__(widget, index)