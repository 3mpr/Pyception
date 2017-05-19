import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class QDoubleClickListItem(QObject, QListWidgetItem):
    doubleClicked = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, parent, name):
        QObject.__init__(parent)
        QListWidgetItem.__init__(name)
        self.timer = QTimer()
        self.timer.setSingleShot(True)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()