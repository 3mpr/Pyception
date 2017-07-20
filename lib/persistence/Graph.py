# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 19.07.2017
:Revision: 1
:Status: dev
:Copyright: MIT License
"""

from collections import defaultdict
from heapq import heappop, heappush
from itertools import chain


def flatten(seq):
    if isinstance(seq, str):
        return seq
    if isinstance(seq, list) or isinstance(seq, tuple):
        return list(chain.from_iterable(seq))
    return seq


class GraphException(Exception):
    pass


class Graph(object):

    def __init__(self, direction: bool = True) -> None:
        self._direction = direction
        self._nodes = set()
        self._edges = defaultdict(list)
        self._distances = dict()

    def add(self, node) -> None:
        self._nodes.add(node)

    def connect(self, root, leaf, cost: int = 1) -> None:
        if root not in self._nodes or leaf not in self._nodes:
            raise GraphException("Node does not exist in graph.")
            
        self._edges[root].append(leaf)
        if not self._direction:
            self._edges[leaf].append(root)
        self._distances[(root, leaf)] = cost

    def distance(self, tup: tuple) -> int:
        if tup in self._distances.keys():
            return self._distances[tup]
        elif not self._direction:
            reverse = tuple(reversed(tup))
            if reverse in self._distances.keys():
                return self._distances[reverse]
        return float("inf")

    def path(self, source, dest) -> float and list:
        queue, visited = [(0, source, ())], set()
        while queue:
            cost, vsrc, path = heappop(queue)
            if vsrc not in visited:
                visited.add(vsrc)
                path = list(path)
                path.insert(0, vsrc)

                if vsrc == dest:
                    return cost, list(reversed(path))

                for vdst in self._edges.get(vsrc, source):
                    if vdst not in visited:
                        pcost = cost + self.distance((vsrc, vdst))
                        heappush(queue, (pcost, vdst, path))

        return float("inf"), []
