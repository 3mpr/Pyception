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
from lib.pattern import Singleton
from lib import workdir


RESET = "\033[0m"


class Level(Enum):
    EXCEPTION = 0
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    DEBUG = 4
    TRACE = 5
    FAILED = 20
    DONE = 21


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

    def __init__(self, output_level: Level = Level.INFORMATION):
        """
        Class constructor. Initializes the logging output level an detect
        whether the script is running on a windows or unix platform.

        :param output_level:    The stdout verbosity of the logging.
        :type output_level:     Level
        """
        self.output_level = output_level
        self._print = self._print_nt if os.name == 'nt' else self._print_unix

        fout_path = os.path.join(
            workdir,
            strftime("%y-%m-%d.log", gmtime())
        )
        self._file_out = open(fout_path, "a+")
        self._last_output_level = None

# --------------------------------------------------------------------- METHODS

    def log(self, message: str, lvl: Level = Level.INFORMATION,
            linesep: str = os.linesep):
        """
        Main class method, logs the messages.

        :param message:     The text to be logged.
        :param lvl:         The level of the message.
        :type message:      str
        :type lvl:          Level
        """
        output = self._print(message, lvl)

        if lvl == Level.DONE or lvl == lvl.FAILED:
            lvl = self._last_output_level

        if lvl.value <= self.output_level.value:
            print(output, end=linesep)
        self._file_out.write(output + linesep)

        self._last_output_level = lvl

    def _print_nt(self, text: str, lvl: Level = Level.INFORMATION,
                  linesep: str = os.linesep):
        """
        Windows stdout logging. Without colors.
        """
        if lvl == Level.INFORMATION:
            return "Info: %s" % text
        elif lvl == Level.WARNING:
            return "Warning: %s" % text
        elif lvl == Level.ERROR:
            return "Error: %s" % text
        elif lvl == Level.EXCEPTION:
            return "EXCEPTION: %s" % text
        elif lvl == Level.DONE:
            return " %s ✔" % text
        elif lvl == Level.FAILED:
            return " %s ✘" % text

    def _print_unix(self, text: str = "", lvl: Level = Level.INFORMATION,
                    linesep: str = os.linesep):
        """
        UNIX stdout logging. With colors.
        """
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
        elif lvl == Level.DEBUG:
            prefix = "Debug :"
            color = Color.WHITE.value

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
        return message.ljust(110)
