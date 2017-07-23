# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 04.07.2017
:Status: dev
:Copyright: MIT License
"""

import os
import re
from .path import rlistdir


class ResourceCollection(object):
    """
    Simple helper class, represents a directory and file type association.
    Its purpose is to short-circuit repetitive file manipulation tasks.

    TODO documentation
    """
    def __init__(self, directory: str, extensions: str or list) -> None:
        self.directory = directory
        if not isinstance(extensions, list):
            self.extensions = list()
            self.extensions.append(extensions)
        else:
            self.extensions = extensions

    def __len__(self):
        return len(self.list())

    def _has(self, file: str) -> bool:
        for f in self.list():
            if file == os.path.basename(f):
                return True
        return False

    def _suffix(self, file: str):
        for extension in self.extensions:
            yield file + extension

    def list(self, short: bool = False) -> list:
        """
        List every file this resource collection has.
        The listing is recursive.

        :param short:   Whether to return the full path of the files or not.
        :type short:    bool
        :return:        The files
        :rtype:         list
        """
        files = rlistdir(self.directory, self._filter)
        if not short:
            return files
        return [os.path.basename(file_) for file_ in files]

    def find(self, expr: str) -> list:
        """
        TODO
        """
        return [file_ for file_ in self.list(True) if re.search(expr, file_)]

    def has(self, file: str) -> bool:
        """
        Returns whether this ResourceCollection has the file <file> or not.
        If the file is provided without extension, the ResourceCollection will
        attempt to resolve it with internal extensions.

        :param file:    The searched file
        :type file:     str
        :return:        Whether this ResourceCollection has the searched file
                        or not
        :rtype:         bool
        """
        if len(file.split(".")) > 1:
            return self._has(file)
        for posfile in self._suffix(file):
            if self._has(posfile):
                return True
        return False

    def get(self, file: str) -> str:
        """
        Returns the path of the file <file>.
        If the file is provided without extension, the ResourceCollection will
        attempt to resolve it with internal extensions and return the first
        suffixed file found if any. This method raise IOError if the searched
        file does not exist in this ResourceCollection.

        :param file:    The searched file
        :type file:     str
        :return:        The file path
        :rtype:         str

        :raise IOError
        """
        if not self.has(file):
            raise IOError("File {} does not exist in {}.".format(
                file, self.directory
            ))

        if len(file.split(".")) > 1:
            for f in self.list():
                if file == os.path.basename(f):
                    return f

        for posfile in self._suffix(file):
            for f in self.list():
                if posfile == os.path.basename(f):
                    return f

    def _filter(self, files: list):
        retval = list()
        for file in files:
            if self._has_extension(file):
                retval.append(file)
        return retval

    def _has_extension(self, file: str):
        file = file.split("/")[-1]
        file.strip(".")
        file_parts = file.split(".")
        file_parts.pop(0)
        extension = "".join("." + part for part in file_parts)
        return extension in self.extensions
