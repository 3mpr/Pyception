#!/usr/bin/env python

"""
Part of the <Perception> package.

created: 16.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 21.03.2017
"""

import os
import signal
import sys
import time

import blessed

from Perception.Data.Operators.TimeInterface import TimedPaper
from Perception.Data.Repository import Repository
from Perception.Design.Command import Command
from Perception.Design.CommandStack import CommandStack
from Perception.helpers import Cursor
from Perception.helpers import clearline
from Perception.helpers import echo
from Perception.helpers import readline
from Perception.helpers import write


class Interpret(object):
    """
    Project entry point.

    This class handles a big chunk of the application logic by implementing a basic Command Pattern.
    Commands are stacked on top of each other, leaving a stack returns the user back to the command
    called right before it.

    It also handles a big part of the model to view correlation.
    """
# ------------------------------------------------------------------------------------------- MAGIC

    def __init__(self):
        # Main terminal components
        self.TERM = blessed.Terminal()
        self.position = Cursor(y=1, x=1, term=self.TERM)

        # Configuration & File/Directory handling
        self._repo = Repository("perception.yml")

        # Signals handling
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTSTP, self.pop_action)

        # Interaction options
        self._main_options = [
            Command(self.pull, {}, "Import file for analysis"),
            Command(self.explore, {}, "Explore imported experiments"),
            Command(self.exit, {}, "Exit")
        ]

        # First command
        self._command_stack = CommandStack()
        self._command_stack.add(Command(
            self.menu,
            {'options': self._main_options, 'section': "Main Menu"},
            ""
        ))

# ----------------------------------------------------------------------------------------- METHODS

    # ----------------------------------------------------------- CONTROL LOGIC

    def run(self):
        # type: () -> None
        """
        Main class method.
        Will be active as long as the internal CommandStack is not empty
        """
        while not self._command_stack.empty():
            self._command_stack.top().execute()
        self.exit()

    def input(self, timeout=None):
        """
        Simple Terminal.inkey() shorthand. Used often enough to justify a method.

        :param timeout: Terminal.inkey is a blocking function, the timeout tells the function for
                        how long to wait before to stop awaiting for an input.
        :return: char   The key pressed.
        """
        with self.TERM.cbreak():
            return self.TERM.inkey(timeout)

            # ----------------------------------------------------------------------------------------- SIGNALS

    def exit(self, signum=None, frame=None):
        # type: (int, Frame) -> None
        """
        Prints a message before to exit the application.

        :param signum: int  The calling signal if any.
        :param frame: TODO
        """
        write(Cursor(x=2, y=self.TERM.height - 1, term=self.TERM), "{t.bold}{t.red}Terminating...")
        sys.exit(0)

    def pop_action(self, signum=None, frame=None):
        """
        Signal version of the CommandStack.pop() method.

        :param signum: int  The calling signal if any.
        :param frame: TODO
        """

        self._command_stack.pop()

    # ----------------------------------------------------------- DISPLAY LOGIC

    def header(self, section, x, y):
        """
        Displays a header for the given section on the terminal.

        :param section: string  name
        :param x: int           x-axis position
        :param y: int           y-axis position
        """
        write(
            Cursor(x=x, y=y, term=self.TERM),
            "{t.green}{t.bold}PERCEPTION {t.white}SHELL : {t.normal}{section}",
            {'section': section}
        )

    def menu(self, options, offset_y=2, offset_x=2, section=""):
        """
        Prints a basic menu to the user, key press is then returned to the calling function.

        :param options: Dictionary  The options to display
        :param offset_y: int        The Y-axis offset to print before the first element
        :param offset_x: int        The X-axis offset to print before every elements
        :param section: string      The section name (for the header)
        """
        positions = [Cursor(y=y+offset_y + 2, x=offset_x + 2, term=self.TERM) for y in range(len(options))]
        while self._command_stack.top().name == self.menu.__name__:
            echo(self.TERM.home + self.TERM.clear)
            self.header(section, offset_x, offset_y)

            for index in range(len(options)):
                write(
                    positions[index],
                    "{t.bold}{index}){t.normal} {entry}{separator}",
                    {
                        'index': index + 1,
                        'entry': options[index].description,
                        'separator': "." if index == len(options) - 1 else " ;"
                    }
                )
            inp = self.input(0.1)

            if inp is None or inp == "":
                continue

            if ord(str(inp)) == 24 or ord(str(inp)) == 27:
                self._command_stack.pop()
                break

            try:
                choice = int(str(inp))

                if choice - 1 in options:
                    self._command_stack.add(options[choice - 1])
                    break
            except ValueError:
                pass

# --------------------------------------------------------------- CONTROL LOGIC

    # -------------------------------------------------------------- DATA LOGIC

    def pull(self):
        """
        Handles file importation.

        TODO REFACTOR
        """
        imported = False
        path_error = False
        annotation_location = Cursor(y=6, x=2, term=self.TERM)
        file_path = ""
        lasted = 0.0
        paper = None

        while not imported:
            echo(self.TERM.home + self.TERM.clear())

            self.header("Import", 2, 2)
            if path_error:
                write(annotation_location, "{t.bold}{t.red}Specified file does not exist.", {})
            write(Cursor(y=4, x=4, term=self.TERM), "{t.bold}{t.white}Location : {t.normal}", {})

            file_path = readline(self.TERM)
            write(annotation_location, "{t.bold}Importing file...")

            lasted = time.time()
            paper = self._repo.fetch(file_path)
            lasted = time.time() - lasted

            path_error = paper is None
            if paper is not None:
                self._command_stack.pop()
                imported = True

                clearline(self.TERM, 6)
                write(annotation_location, "{t.bold}Importing file...")

        write(Cursor(y=6, x=19, term=self.TERM), " Done.", {})

        write(
            Cursor(y=7, x=2, term=self.TERM),
            "Imported file {path} in {time:.2f}s.",
            {'path': file_path, 'time': lasted}
        )

        recommended_path = os.path.join(
            os.getcwd(),
            os.path.basename(os.path.splitext(file_path)[0])
        )

        self.menu(
            {
                0: ("Show file details", self.details, {
                    'paper': paper
                }), 1: ("Save updated file", self.save, {
                    'offset_x': 2,
                    'offset_y': 8,
                    'paper': paper,
                    'recommended': recommended_path
                }), 2: ("Return", self.pull, {})
            }
        )

    def save(self, paper, offset_x, offset_y, recommended=None):
        """
        Handles the saving interaction with the user.
        A base/recommended destination folder can be specified.


        :param paper: Transaction     The paper to be saved
        :param offset_x:        X-axis position of the saving message
        :param offset_y:        y-axis position of the saving message
        :param recommended:     The recommended destination folder.
        """
        write(
            Cursor(x=offset_x, y=offset_y, term=self.TERM),
            "{t.bold}{t.white}Path {recommended}: {t.normal}",
            {'recommended': "" if recommended is None else "(" + recommended + ")"}
        )

        directory = readline(self.TERM)
        directory = recommended if directory == u'' or directory is None else directory

        chain = "Saving in {directory}...".format(directory=directory)
        chain_length = len(chain)

        write(Cursor(x=offset_x, y=offset_y+1, term=self.TERM), chain)

        self._repo.save_subject(paper, directory)

        write(Cursor(x=offset_x + chain_length, y=offset_y+1, term=self.TERM), "Done.")

        self._command_stack.pop()

    def details(self, paper, offset_x, offset_y):
        # type: (TimedPaper, int, int) -> None
        data = list()
        data.extend([
            {'title': "NB RECORDS", 'value': paper.count()},
            {'title': "LENGTH(s)", 'value': paper.time()},
            {'title': "CHUNKED", 'value': paper.is_chunked()},
            {'title': "EXPERIMENT", 'value': paper.experiment}
        ])

        for index in range(len(data)):
            write(
                Cursor(x=offset_x, y=offset_y+index, term=self.TERM),
                "{t.white}{t.bold}{title} : {value}",
                data[index]
            )

    def explore(self):
        pass

# -------------------------------------------------------------------------------------- PROPERTIES

if __name__ == "__main__":
    ITR = Interpret()
    ITR.run()
