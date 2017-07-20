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

import sqlite3
from collections import OrderedDict
import re
from .Graph import Graph

class LastUpdatedOrderedDict(OrderedDict):
    'Store items in the order the keys were last added'

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)

class DBSchema(object):

    _schema_query = "SELECT sql FROM sqlite_master WHERE type='table';"

    def __init__(self, db_conn: sqlite3.Connection) -> None:
        self.db_conn = db_conn
        self._graph = Graph(direction=False)
        self._foreign_keys = dict()

        cursor = db_conn.execute(self._schema_query)
        schemas = [dict(cell)["sql"] for cell in cursor.fetchall()]
        for schema in schemas:
            self._analyze_schema(schema)

    def _analyze_schema(self, schema: str) -> None:
        schema_lines = schema.splitlines()

        re_groups = re.match(
            ".*CREATE TABLE (.*)", schema_lines[0]
        ).groups()
        name = re_groups[0].strip(" ()\´`")
        self._graph.add(name)
        schema_lines.pop(0)

        for line in schema_lines:
            regex = re.match(
                ".*FOREIGN KEY \((.*)\) REFERENCES (.*) \((.*)\).*", line
            )

            if not regex:
                continue
            results = regex.groups()
            results = [result.strip(" ()\´`") for result in results]

            self._graph.add(results[1])
            self._graph.connect(name, results[1])

            self._foreign_keys[(name, results[1])] = (
                results[0], results[2]
            )

    def path(self, table_one: str, table_two: str) -> dict:
        _, table_path = self._graph.path(table_one, table_two)
        if not table_path:
            return None
        retval = LastUpdatedOrderedDict()
        for index, milestone in enumerate(table_path):
            if index == len(table_path) - 1:
                break
            retval[(milestone, table_path[index + 1])] = self.link(
                milestone, table_path[index + 1]
            )
        return retval

    def link(self, table_one: str, table_two: str) -> tuple:
        tup = (table_one, table_two)
        if tup in self._foreign_keys.keys():
            return self._foreign_keys[tup]

        reverse = tuple(reversed(tup))
        if reverse in self._foreign_keys.keys():
            return tuple(reversed(self._foreign_keys[reverse]))

    def columns(self, table: str) -> list:
        """
        Pull the column names of the **table** table.

        :param table:   The table name.
        :type table:    str
        :return:        The list of names
        :rtype:         list
        """
        cursor = self.db_conn.execute("SELECT * FROM {0}".format(table))
        return [description[0] for description in cursor.description]

    @property
    def tables(self) -> list:
        cursor = self.db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )

        return [item for sublist in cursor.fetchall() for item in sublist]
