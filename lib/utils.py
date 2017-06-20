import os
from enum import Enum
import lib.pattern as pattern
from time import gmtime, strftime


RESET = "\033[0m"


class Level(Enum):
    INFORMATION = 0
    WARNING = 1
    ERROR = 2
    EXCEPTION = 3
    DONE = 4
    FAILED = 7
    CR_MESSAGE = 5


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

    __metaclass__ = pattern.Singleton

    def __init__(self):
        self._print = self._print_nt if os.name == 'nt' else self._print_unix

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
        if lvl == Level.INFORMATION:
            fmt = str(Style.BOLD.value) + str(Color.BLUE.value) + "Info:"
        elif lvl == Level.WARNING:
            fmt = str(Style.BOLD.value) + str(Color.ORANGE.value) \
                      + "Warning:"
        elif lvl == Level.ERROR:
            fmt = str(Style.BOLD.value) + str(Color.ORANGE.value) + "Error:"
        elif lvl == Level.EXCEPTION:
            fmt = "\n" + str(Style.BOLD.value) + str(Background.RED.value) \
                  + str(Color.WHITE.value) + "EXCEPTION:"
        elif lvl == Level.DONE:
            print(str(Style.BOLD.value) + str(Color.GREEN.value) + text + " ✔"
                  + str(RESET))
            return
        elif lvl == Level.FAILED:
            print(str(Style.BOLD.value) + str(Color.ORANGE.value) + text + " ✘"
                  + str(RESET))
            return
        fmt += str(RESET)

        output = strftime("[%m-%d %H:%M:%S]", gmtime()) + " - " + fmt + " " \
                                                        + text
        output = output.ljust(110)
        print(output, end=linesep)


logger = Logger()
log = logger.log


def progress(pre: str, action: tuple, post: str = " Done",
             raise_ex: bool = False) -> object:
    """
    TODO
    """
    log(pre, Level.INFORMATION, "")
    retval = None
    try:
        retval = action[0](**action[1])
    except Exception as e:
        log(e, Level.EXCEPTION)
        if raise_ex:
            raise e
        return
    log(post, Level.DONE)
    return retval
