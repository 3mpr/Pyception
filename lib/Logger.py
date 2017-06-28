# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 24.06.2017
:Revision: 2
:Copyright: MIT License
"""

import os
from enum import Enum
from time import gmtime, strftime
from lib import Singleton


RESET = "\033[0m"


class Level(Enum):
    INFORMATION = 0
    WARNING = 1
    ERROR = 2
    EXCEPTION = 3
    DONE = 4
    CR_MESSAGE = 5
    FAILED = 6


class Color(Enum):
    PINK = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[33m"
    RED = "\033[91m"
    GREY = "\033[91m"
    WHITE = "\u001b[37;1m"


class Background(Enum):
    BLACK = "\u001b[40m"
    RED = "\u001b[41m"
    GREEN = "\u001b[42m"
    YELLOW = "\u001b[43m"
    BLUE = "\u001b[44m"
    MAGENTA = "\u001b[45m"
    CYAN = "\u001b[46m"
    WHITE = "\u001b[47m"


class Style(Enum):
    BOLD = "\u001b[1m"
    REVERSED = "\u001b[7m"
    UNDERLINE = "\u001b[4m"


def bold(text: str) -> str:
    return Style.BOLD.value + text + RESET


class Logger(object):

    __metaclass__ = Singleton

# ----------------------------------------------------------------------- MAGIC

    def __init__(self):
        self._print = self._print_nt if os.name == 'nt' else self._print_unix

# --------------------------------------------------------------------- METHODS

    def log(self, text: str, lvl: Level = Level.INFORMATION,
            linesep: str = os.linesep):
        self._print(text, lvl, linesep)

    def _print_nt(self, text: str, lvl: Level = Level.INFORMATION,
                  linesep: str = os.linesep):
        if lvl == Level.INFORMATION:
            print("Info: %s" % text, end=linesep)
        elif lvl == Level.WARNING:
            print("Warning: %s" % text, end=linesep)
        elif lvl == Level.ERROR:
            print("Error: %s" % text, end=linesep)
        elif lvl == Level.EXCEPTION:
            print("EXCEPTION: %s" % text, end=linesep)
        elif lvl == Level.DONE:
            print(" %s" % text, end=linesep)

    def _print_unix(self, text: str = "", lvl: Level = Level.INFORMATION,
                    linesep: str = os.linesep):
        prefix = ""
        suffix = ""
        color = RESET

        if lvl == Level.INFORMATION:
            prefix = "Info :"
            color = Color.BLUE.value
        elif lvl == Level.WARNING:
            prefix = "Warning :"
            color = Color.ORANGE.value
        elif lvl == Level.ERROR:
            prefix = "Error :"
            color = Color.RED.value
        elif lvl == Level.EXCEPTION:
            prefix = "EXCEPTION :"
            color = Background.RED.value + Color.WHITE.value
        elif lvl == Level.DONE:
            suffix = " ✔"
            color = Color.GREEN.value
        elif lvl == Level.FAILED:
            suffix = " ✘"
            color = Color.ORANGE.value

        message = "{bold}{color}{prefix} {text} {suffix}{reset}".format(
            bold=Style.BOLD.value,
            color=color,
            prefix=prefix,
            text=text,
            suffix=suffix,
            reset=RESET
        )
        if lvl is not Level.DONE and lvl is not Level.FAILED:
            message = strftime("[%y-%m-%d %H:%M:%S] - ", gmtime()) + message
        output = message.ljust(110)

        print(output, end=linesep)
