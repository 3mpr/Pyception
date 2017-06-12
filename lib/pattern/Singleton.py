"""
Part of the <Perception> package.

created: 15.03.2017
author: Florian Indot <florian.indot@gmail.com>
last updated: never
"""


class Singleton(type):
    """
    Singleton metaclass.
    
    Handles calls to instances to check for existence in intern dictionary. If the class
    reference is not present, create it, then return it. If it is, skip creation and returns
    folded instance reference.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
