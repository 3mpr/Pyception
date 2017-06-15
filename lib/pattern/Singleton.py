# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 15.03.2017
:Revision: 1
:Copyright: MIT License
"""


class Singleton(type):
    """
    Singleton metaclass.

    Handles calls to instances to check for existence in intern dictionary.
    If the class reference is not present, create it, then return it. If it is,
    skip creation and returns folded instance reference.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args,
                **kwargs
            )
        return cls._instances[cls]
