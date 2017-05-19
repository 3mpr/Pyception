#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 02.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 16.04.2017
"""

import sys
import os

from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QStackedWidget, QDesktopWidget, QPushButton, QGroupBox
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine

from Perception.GUI.InteractiveQGroupBox import InteractiveQGroupBox
from Perception.GUI.InteractiveQLabel import InteractiveQLabel

from Perception import conf
from Perception.GUI.Section import Section
from Perception.GUI.SectionImportExport import SectionImportExport
from Perception.GUI.Category import Category


class App(object):

    registered = False

    """
    Application entry point.
    """
    def __init__(self) -> None:
        """
        Initializes various Qt Application components and behaviours.
        """
        self.app = QApplication(sys.argv)
        self.engine = QQmlEngine()
        if not App.registered:
            print("Registering...")
            App.register()

        self.window = uic.loadUi(os.path.join(conf.UI_PATH, "app.ui"))
        self.window.title = "Perception"

        stack = self.window.findChild(QStackedWidget, "Content")
        self.sections = Category(stack)

        self.resources = {
            'icons': conf.ICONS,
            'gui': conf.UI_FILES,
            'css': conf.STYLES
        }

        self.sections.append([
            SectionImportExport()
        ])

        self.center()
        self.style()
        self.sidebar()

    def style(self) -> None:
        """
        Adds css to the application.
        """
        file = self.resources["css"].get("master")
        with open(file, "r") as css:
            stylesheet = css.read()
        self.window.setStyleSheet(stylesheet)

    def center(self) -> None:
        """
        Centers the window.
        """
        frame_geometry = self.window.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.window.move(frame_geometry.topLeft())

    def sidebar(self) -> None:
        """
        Initializes the sidebar logic.
        """
        sidebar = self.window.findChild(QGroupBox, "Sidebar")
        buttons = sidebar.findChildren(QPushButton)

        for button in buttons:
            button_name = button.objectName()
            button_func = self.sections.set_to(button_name)
            button.clicked.connect(button_func)

    @staticmethod
    def register() -> None:
        qmlRegisterType(
            InteractiveQGroupBox,
            "InteractiveQGroupBox",
            1, 0,
            "IQGroupBox"
        )

        qmlRegisterType(
            InteractiveQLabel,
            "InteractiveQLabel",
            1, 0,
            "IQLabel"
        )

        App.registered = True

    def run(self) -> int:
        self.window.show()
        return self.app.exec_()
