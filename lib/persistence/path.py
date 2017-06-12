# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 09.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 12.06.2017
"""

import os
if os.name == 'nt':
    import win32api
    import win32con

PWD = os.path.dirname(os.path.realpath(__file__))

# ------------------------------------------------------------------- FUNCTIONS


def is_hidden(path: str) -> bool:
    """
    Returns whether the file at <path> is a hidden file or not.
    :param path: str The file path
    :return: bool
    """
    if os.name == 'nt':
        attribute = win32api.GetFileAttributes(path)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN
                            | win32con.FILE_ATTRIBUTE_SYSTEM)
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
    Returns the parent directory of <directory>.
    Used often enough to justify a function.
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
