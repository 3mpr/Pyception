# -*- coding: utf-8 -*-

"""
Part of the <Perception> package.

created: 18.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: 21.03.2017
"""

class Command(object):

    def __init__(self, function, kwargs, description=""):
        self._function = function
        self._kwargs = kwargs
        self._description = description

    def execute(self):
        return self._function(**self._kwargs)

    @property
    def name(self):
        return self._function.__name__

    @property
    def description(self, description=None):
        if description is None:
            return self._description
        else:
            self._description = description
