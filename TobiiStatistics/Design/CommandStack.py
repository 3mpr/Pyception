# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 18.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""

from Perception.Design.Command import Command

dummy_command = Command(lambda: {}, {})

class CommandStack(object):

    def __init__(self):
        self._commands = list()

    def add(self, command):
        assert isinstance(command, Command), "CommandStack only allows commands."
        self._commands.append(command)

    def pop(self):
        return self._commands.pop()

    def depth(self):
        return len(self._commands)

    def top(self):
        try:
            command = self._commands[len(self._commands) - 1]
        except IndexError:
            # Stack is empty
            command = dummy_command
        return command

    def empty(self):
        return len(self._commands) == 0

    def is_active(self, func_name):
        return self.top().name == func_name
