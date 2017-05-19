# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 14.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 16.04.2017
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTextEdit, QCheckBox, QPushButton, QVBoxLayout

from Perception.helpers import children
from Perception import conf
from Perception.Data.Path import *
from .Section import Section
from .InteractiveQLabel import InteractiveQLabel


class SectionPicker(Section):
    """
    Simple file picker implementation.
    """
    highlight_color = "#033649"
    sec_fx = "background-color: " + highlight_color

    fopen = pyqtSignal()

# ------------------------------------------------------------------------------------------- MAGIC

    @staticmethod
    def cast(section):
        __doc__ = Section.__doc__
        return SectionPicker(section.name)

    def load(self) -> None:
        __doc__ = Section.load.__doc__
        super().load()

        self.w_directory = self.find(QWidget, "Files")
        self.w_target = self.find(QTextEdit, "Path")
        self.w_hidden = self.find(QCheckBox, "ShowHidden")
        self.w_import = self.find(QPushButton, "ImportButton")

        self.w_hidden.stateChanged.connect(self.toggle_hidden)
        self.w_import.mousePressEvent = self.fopen.emit

        os.chdir(os.path.expanduser("~"))
        self.listdir()

    def __init__(self, name: str) -> None:
        super().__init__(conf.UI_FILES.get("Picker"), name)
        self.show_hidden = False

        self.w_directory = None
        self.w_target = None
        self.w_hidden = None
        self.w_import = None

# ----------------------------------------------------------------------------------------- METHODS

    def toggle_hidden(self, display: bool = None) -> None:
        """
        Toggles hidden files display in this picker.
        """
        display = not self.show_hidden if display is None else display
        self.show_hidden = display
        self.cleardir()
        self.listdir()

    def _make_dir_entry(self, parent: QWidget, path: str, name: str = None) -> InteractiveQLabel:
        """
        Makes an InteractiveQLabel attached to the QWidget <parent> with the text content <path>.
        Then connects it to self.select_dir and (simple click) and self.change_dir (double click).
        
        :param parent: QWidget The parent widget
        :param path: str The label content 
        :return: InteractiveQLabel The new label
        """
        name = path if name is None else name

        def secdir(widget: InteractiveQLabel, target: str) -> callable:
            return lambda: self.secdir(widget, target)

        def chdir(target: str) -> callable:
            return lambda: self.chdir(target)

        w_entry = InteractiveQLabel(name, parent)
        w_entry.clicked.connect(secdir(w_entry, path))
        w_entry.doubleClicked.connect(chdir(path))

        return w_entry

    def listdir(self) -> None:
        """
        List the current directory content in the main picker widget <self.w_directory>.        
        """
        if self.w_directory.layout() is not None:
            QWidget().setLayout(self.w_directory.layout())
        layout = QVBoxLayout(self.w_directory)
        layout.setAlignment(Qt.AlignTop)

        w = self._make_dir_entry(self.w_directory, pardir(os.getcwd()), "..")
        layout.addWidget(w)

        files = listdir(os.getcwd(), None if self.show_hidden else remove_hidden)
        for file in files:
            w = self._make_dir_entry(self.w_directory, file)
            layout.addWidget(w)

        self.w_directory.setLayout(layout)

    def secdir(self, widget: InteractiveQLabel, target: str) -> None:
        """
        Apply the visual and logical effect of <widget> selection.
        
        :param widget: InteractiveQLabel The selected entry
        :param target: The targeted widget <widget> path.
        """
        for item in children(self.w_directory):
            item.widget().setStyleSheet("")
        widget.setStyleSheet(self.sec_fx)

        path = os.path.join(os.getcwd(), target)
        self.w_target.setText(path)

    def chdir(self, target: str) -> None:
        """
        Changes the current directory and directory display to <target>.
        
        :param target: str The targeted directory.
        """
        if os.path.isfile(target):
            return

        os.chdir(target)
        self.w_target.setText(os.getcwd())
        self.cleardir()
        self.listdir()

    def cleardir(self) -> None:
        """
        Clears the current path entry widgets.
        """
        items = children(self.w_directory)

        for item in items:
            widget = item.widget()
            self.w_directory.layout().removeWidget(widget)
            widget.deleteLater()
            widget = None

    def open_file(self, event):
        self.fopen.emit()
        pass

# -------------------------------------------------------------------------------------- PROPERTIES
