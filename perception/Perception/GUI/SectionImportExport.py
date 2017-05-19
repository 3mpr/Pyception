# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 03.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 08.04.2017
"""

import os

from PyQt5.QtWidgets import QStackedWidget, QGroupBox

from Perception import conf
from . import InteractiveQGroupBox
from . import Category
from . import Section
from . import SectionPicker


class SectionImportExport(Section):
    __doc__ = Section.__doc__
    """
    This section holds the whole import  export logic.
    """

# ------------------------------------------------------------------------------------------- MAGIC

    @staticmethod
    def cast(section: Section):
        __doc__ = Section.__doc__
        return SectionImportExport()

    def load(self):
        super().load()

        self.io_box = Category(
            self.widget.findChild(QStackedWidget, "FileOperations")
        )

        filepicker = SectionPicker("PickFile")
        folderpicker = SectionPicker("PickFolder")
        #filepicker.fopen.connect()
        #folderpicker.fopen.connect()

        self.io_box.append([filepicker, folderpicker])

        self.w_open_file = self.find(QGroupBox, "OpenFile")
        self.w_open_file.clicked.connect(self.io_box.set_to("PickFile"))

        self.w_open_folder = InteractiveQGroupBox(self.find(QGroupBox, "OpenFolder"))
        self.w_open_folder.clicked.connect(self.io_box.set_to("PickFolder"))

    def __init__(self) -> None:
        super().__init__(conf.UI_FILES.get("IO"), "IO")
        self.io_box = None
        self.w_open_file = None
        self.w_open_folder = None

# ----------------------------------------------------------------------------------------- METHODS

# -------------------------------------------------------------------------------------- PROPERTIES
