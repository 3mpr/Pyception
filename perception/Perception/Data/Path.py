# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 09.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 15.04.2017
"""

import os
if os.name == 'nt':
    import win32api, win32con

PWD = os.path.dirname(os.path.realpath(__file__))

# ------------------------------------------------------------------------------------------------------------ FUNCTIONS


def is_hidden(path: str) -> bool:
    """
    Returns whether the file at <path> is a hidden file or not.
    :param path: str The file path
    :return: bool
    """
    if os.name == 'nt':
        attribute = win32api.GetFileAttributes(path)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    else:
        return path.startswith('.')


def remove_hidden(files: list) -> list:
    """
    Removes the hidden files from path list <files>.
    :param files: list The file paths
    :return: list The file paths without hidden files.
    """
    no_hidden = list()
    for file in files:
        if not is_hidden(file):
            no_hidden.append(file)
    return no_hidden


def pardir(directory: str) -> str:
    """
    Returns the parent directory of <directory>. Used often enough to justify a function.
    :param directory: str The directory
    :return: str The parent directory
    """
    return os.path.abspath(os.path.join(directory, os.pardir))


def find(file: str, directory: str) -> list:
    """
    Recursively search for a file in the given directory.
    :param file: str The searched file
    :param directory: str The top directory of the search
    :return: list The found absolute paths
    """
    inter_dir = directory
    founds = list()

    stack = list()
    stack.append(os.listdir(directory))

    while len(stack):
        for f in stack[-1]:
            stack[-1].remove(f)
            abs_path = os.path.join(inter_dir, f)

            if not os.access(abs_path, os.R_OK) or os.path.islink(abs_path):
                continue
            if os.path.isdir(abs_path):
                inter_dir = os.path.join(inter_dir, abs_path)
                stack.append(os.listdir(abs_path))
                break
            if f == file:
                founds.append(abs_path)

        if not len(stack[-1]):
            inter_dir = pardir(inter_dir)
            stack.pop()

    return founds


def rlistdir(directory: str, filter_callback: callable = None) -> list:
    """
    Recursively list all the content of <directory>.
    :param directory: str The listed directory
    :param filter_callback: A given result filter
    :return: list The found content
    """
    if not directory.startswith("/"):
        directory = os.path.join(os.getcwd(), directory)

    inter_dir = directory
    files = list()

    stack = list()
    stack.append(os.listdir(directory))

    while len(stack):
        for f in stack[-1]:
            stack[-1].remove(f)
            abs_path = os.path.join(inter_dir, f)

            if not os.access(abs_path, os.R_OK) or os.path.islink(abs_path):
                continue
            if os.path.isdir(abs_path):
                inter_dir = os.path.join(inter_dir, abs_path)
                stack.append(os.listdir(inter_dir))
                break

            files.append(abs_path)

        if not len(stack[-1]):
            inter_dir = pardir(inter_dir)
            stack.pop()

    files = sorted(files)
    if filter_callback is None:
        return files
    return filter_callback(files)


def listdir(directory: str, filter_callback: callable = None) -> list:
    files = sorted(os.listdir(directory))
    if filter_callback is None:
        return files
    return filter_callback(files)


# -------------------------------------------------------------------------------------------------------------- CLASSES


class ResourceCollection(object):
    """
    Simple helper class, represents a directory and file type association.
    Its purpose is to short-circuit repetitive file manipulation tasks.
    """
    def __init__(self, directory: str, extensions: str or list) -> None:
        self.directory = directory
        if not isinstance(extensions, list):
            self.extensions = list()
            self.extensions.append(extensions)
        else:
            self.extensions = extensions

    def _has(self, file: str) -> bool:
        for f in self.list():
            if file == os.path.basename(f):
                return True
        return False

    def _suffix(self, file: str):
        for extension in self.extensions:
            yield file + extension

    def list(self) -> list:
        """
        List every file this resource collection has.
        The listing is recursive.

        :return: list The files
        """
        return rlistdir(self.directory, self._filter)

    def has(self, file: str) -> bool:
        """
        Returns whether this ResourceCollection has the file <file> or not.
        If the file is provided without extension, the ResourceCollection will attempt
        to resolve it with internal extensions.

        :param file: str The searched file
        :return: bool Whether this ResourceCollection has the searched file or not
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
        If the file is provided without extension, the ResourceCollection will attempt
        to resolve it with internal extensions and return the first suffixed file found if any.
        This method raise IOError if the searched file does not exist in this ResourceCollection.

        :param file: str The searched file
        :return: The file path

        :raise IOError
        """
        if not self.has(file):
            raise IOError("File {} does not exist in {}.".format(file, self.directory))

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
        file.strip(".")
        file_parts = file.split(".")
        file_parts.pop(0)
        extension = "".join("." + part for part in file_parts)
        return extension in self.extensions

