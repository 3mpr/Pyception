# -*- coding: utf-8 -*-

"""
Written the 12/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

from Point import Point
from Area import Area

class Analyst(object):

    def __init__(self):
        print "do smth"

    @staticmethod
    def watch(fin, completion_fields):
        """
        TODO
        """
        watched = fin.count()
        for record in fin.record():
            for field in completion_fields:
                if not record[field]:
                    watched = watched - 1
                    break
        return watched, (float(watched) / float(fin.count()))

    @staticmethod
    def stare(fin, point_field, area):
        """
        TODO
        """
        stared = fin.count()
        for record in fin.record():
            point = Point.create(record[point_field])
            if not area.contains(point):
                stared = stared - 1
        return stared, (float(stared) / float(fin.count()))
