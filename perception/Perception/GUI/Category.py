# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 14.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: never
"""

from PyQt5.QtWidgets import QStackedWidget

from overload import *

from Perception.Data import OrderedDict
from Perception.GUI.Section import Section


class Category(object):
    """
    Wraps the QStackedWidget in a friendly API.
    """
    def __init__(self, stack: QStackedWidget) -> None:
        assert isinstance(stack, QStackedWidget), "Expected QStackedWidget, received {}.".format(type(stack))

        self._stack = stack
        self._sections = OrderedDict([], [])
        self._current_section = 0
        self._nb_sections = self._stack.count()

    def append(self, sections: list) -> None:
        for section in sections:
            assert issubclass(section.__class__, Section), "Expected Section, received {}.".format(section.__class__)
            self._sections[section.name] = section

    def remove(self, section: Section) -> Section:
        """
        Removes a section from this category.
        :param section: Section The removed section.
        :return: Section The removed section.
        """
        if section.name in self._sections:
            ret_section = self._sections[section.name]
            del self._sections[section.name]
            self._stack.removeWidget(section.widget)

            return ret_section

    def count(self) -> int:
        """
        Returns the number of section this category has.
        :return: int The number of sections.
        """
        return len(self._sections)

    def set(self, name: str) -> int:
        """
        Sets the active section to section <name>.
        :param name: str The section name
        :return: int The index of the loaded section
        """
        print("swap to {}".format(name))
        try:
            self._current_section = self._sections.index(name)
        except ValueError as no_header:
            raise ValueError("Section {} does not exist in category.".format(name)) from no_header
        self._load(self._current_section)
        self._stack.setCurrentIndex(self._current_section)

        return self._current_section

    def set_to(self, name):
        return lambda event=None: self.set(name)

    def next(self) -> int:
        """
        Swaps the current active section for the next one.
        :return: int The index of the loaded section
        """
        next_index = 0

        if self._current_section is not self.count() - 1:
            next_index = self._current_section + 1
        self._current_section = next_index
        self._load(next_index)
        self._stack.setCurrentIndex(next_index)

        return self._current_section

    def previous(self) -> int:
        """
        Swaps the current active section for the previous one.
        :return: int The index of the loaded section
        """
        next_index = self.count() - 1
        if self._current_section is not 0:
            next_index = self._current_section - 1
        self._stack.setCurrentIndex(next_index)
        self._current_section = next_index

        return self._current_section

    def _load(self, index: int) -> None:
        """
        Asks to the section specified by index to load itself if it isn't loaded already.
        :param index: int The index of the section
        """
        if not self._sections[index].loaded:
            self._sections[index].load()
            self._stack.addWidget(self._sections[index].widget)
