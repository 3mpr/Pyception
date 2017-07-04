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

import math, inspect
from lib import Logger, Level
from .conf import logging_level


logger = Logger(logging_level)
log = logger.log


def progress(pre: str, action: tuple, post: str = " Done",
             raise_ex: bool = False) -> object:
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


def inheritdoc(cls):
    for base in inspect.getmro(cls):
        if base.__doc__ is not None:
            cls.__doc__ = base.__doc__
            break
    return cls
