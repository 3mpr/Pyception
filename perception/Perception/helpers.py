# -------------------------------------------------------------------------------------------------------------- HELPERS

import sys
import collections
import blessed

from PyQt5.QtWidgets import QWidget

# ------------------------------------------------------------------------------------------- TYPES


Cursor = collections.namedtuple('Cursor', ('y', 'x', 'term'))


# ----------------------------------------------------------------------------------------- CLASSES


class AlarmException(Exception):
    pass


# --------------------------------------------------------------------------------------- FUNCTIONS

def children(widget: QWidget) -> list:
    items = (widget.layout().itemAt(index) for index in range(widget.layout().count()))
    widgets = list()
    for item in items:
        widgets.append(item)
    return widgets

def echo(text):
    # type: (str) -> None
    sys.stdout.write(u'{}'.format(text))
    sys.stdout.flush()


def echo_yx(cursor, text):
    # type: (Cursor, str) -> None
    echo(cursor.term.move(cursor.y, cursor.x) + text)


def write(cursor, text, dictionary=None):
    # type: (Cursor, string, dict) -> None
    dictionary = {} if dictionary is None else dictionary
    echo_yx(cursor, text.format(t=cursor.term, **dictionary))


def readline(term, width=20):
    # type: (blessed.Terminal, int) -> str
    text = u''
    while True:
        inp = term.inkey()
        if inp.code == term.KEY_ENTER:
            break
        elif inp.code == term.KEY_ESCAPE or inp == chr(3):
            text = None
            break
        elif not inp.is_sequence and len(text) < width:
            text += inp
        elif inp.code in (term.KEY_BACKSPACE, term.KEY_DELETE):
            text = text[:-1]
            # https://utcc.utoronto.ca/~cks/space/blog/unix/HowUnixBackspaces
            #
            # "When you hit backspace, the kernel tty line discipline rubs out your previous
            #  character by printing (in the simple case) Ctrl-H, a space, and then another
            #  Ctrl-H."
            echo(u'\b \b')
    return text


def clearline(term, y):
    echo(term.move(y, 1))
    for point in range(term.width):
        echo(" ")