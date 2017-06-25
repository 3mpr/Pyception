# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 25.06.2017
:Revision: 3
:Copyright: MIT License
"""

import math, inspect
from lib import Logger, Level


logger = Logger()
log = logger.log


def progress(pre: str, action: tuple, post: str = " Done",
             raise_ex: bool = False) -> object:
    """
    TODO
    """
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

def inheritdoc(method):
    pass