# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 21.07.2017
:Revision: 1
:Status: dev
:Copyright: MIT License
"""

from collections import defaultdict
from heapq import heappop, heappush
from itertools import chain


def flatten(seq):
    """
    Utility method, shorthand of chain.from_iterable that does not apply
    to strings.
    """
    if isinstance(seq, str):
        return seq
    if isinstance(seq, list) or isinstance(seq, tuple):
        return list(chain.from_iterable(seq))
    return seq


class GraphException(Exception):
    pass


class Graph(object):
    """
    This class is a simple implementation of the graph theory. As such, it
    handles a set of objects in which some pairs of the objects are connected.

    Vertices as from the Graph theory are represented by the **nodes** list
    while their connections, the edges, are represented by the **edges** list.

    Whether the edges are directed or undirectd is specified at object creation.
    """

    def __init__(self, direction: bool = True) -> None:
        """
        Initializes the empty graph.

        :param direction:   Whether the edges are directed or not.
        :type direction:    bool
        """
        self._direction = direction
        self._nodes = set()
        self._edges = defaultdict(list)
        self._distances = dict()

    def add(self, node) -> None:
        """
        Add an unconnected node to the graph.

        :param node:    The new node.
        :type node:     object
        """
        self._nodes.add(node)

    def connect(self, root, leaf, cost: float = 1.0) -> None:
        """
        Connect two nodes and creates and edge. Whether root and leaf can be
        used interchangeably depends on the directionnal nature of the graph
        specified at creation.

        :param root:    node object, must be already present in the graph.
                        It is the starting point of the edge if the graph is
                        directionnal.
        :param leaf:    node object, must be already present in the graph.
                        It is the destination point of the edge if the graph is
                        directionnal.
        :param cost:    The arbitrary price of this edge, used in **path**.
        :type root:     object
        :type leaf:     object
        :type cost:     int
        """
        if root not in self._nodes or leaf not in self._nodes:
            raise GraphException("Node does not exist in graph.")

        self._edges[root].append(leaf)
        if not self._direction:
            self._edges[leaf].append(root)
        self._distances[(root, leaf)] = cost

    def distance(self, tup: tuple) -> float:
        """
        The price of the specified edge. Returns infinity if the edge is not
        found.

        :param tup: The edge
        :type tup:  tuples
        :return:    The edge price
        :rtype:     float
        """
        if tup in self._distances.keys():
            return self._distances[tup]
        elif not self._direction:
            reverse = tuple(reversed(tup))
            if reverse in self._distances.keys():
                return self._distances[reverse]
        return float("inf")

    def path(self, source, dest) -> float and list:
        """
        Heap queue implementation of the Dikstra shortest path algorithm.
        Computes the shortest path between the two specified nodes and its cost
        or infinity and an empty path on failure.

        :param source:  The starting point of the path.
        :param dest:    The seeked destination.
        :type source:   object
        :type dest:     object
        :return:        A cost and list of traversed nodes or infinity an []
                        on failure.
        :rtype:         float and list
        """
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
