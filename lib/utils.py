# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 28.06.2017
:Revision: 4
:Copyright: MIT License
"""

import inspect

def inheritdoc(cls):
    for base in inspect.getmro(cls):
        if base.__doc__ is not None:
            cls.__doc__ = base.__doc__
            break
    return cls
