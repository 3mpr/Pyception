# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 09.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 16.04.2017
"""

from os.path import join

from Perception.Data.Path import *
from Perception.GUI.SectionImportExport import SectionImportExport


PWD = os.path.dirname(os.path.realpath(__file__))

ICON_PATH = join(PWD, "resources", "icons")
STYLE_PATH = join(PWD, "resources", "css")
UI_PATH = join(PWD, "resources", "ui")

ICONS = ResourceCollection(ICON_PATH, [".ico", ".jpeg", ".jpg", ".png"])
STYLES = ResourceCollection(STYLE_PATH, [".css", ".qss"])
UI_FILES = ResourceCollection(UI_PATH, ".ui")

SECTIONS = [
    #{'name': "Graph",      'class': None},
    #{'name': "Info",       'class': None},
    {'name': "IO",          'class': SectionImportExport},
    #{'name': "Server",     'class': None},
    #{'name': "Settings",   'class': None}
]

SECTIONS_IO = [

]
