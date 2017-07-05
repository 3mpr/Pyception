# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 05.06.2017
:Revision: 1
:Copyright: MIT License
"""

import os


class Config(dict):
    """
    Holds named configuration information stored within a python a file.
    """
    def __init__(self, initial: dict = None, name: str = None) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        initial = {} if initial is None else initial
        dict.__init__(self, initial)
        dict.__setattr__(self, "_name", name)

    @staticmethod
    def read(filepath):
        conf = Config()
        deps = {}
        if not os.path.isfile(filepath):
            raise IOError("File %s does not exist." % filepath)
        try:
            file_ = open(filepath, "r")
            exec(file_.read(), deps, conf)
            file_.close()
        except Exception as e:
            print(str(e))
            raise e
        return conf
