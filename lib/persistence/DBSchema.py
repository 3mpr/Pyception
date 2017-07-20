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
import re
from .Graph import Graph


class DBSchema(object):

    _schema_query = "SELECT sql FROM sqlite_master WHERE type='table';"

    def __init__(self, db_conn: sqlite3.Connection) -> None:
        self._graph = Graph(False)
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
            re_groups = re.match(
                ".*FOREIGN KEY \((.*)\) REFERENCES (.*) \((.*)\).*", line
            )

            if not re_groups:
                continue
            re_groups = re_groups.groups()

            self._graph.add(re_groups[1])
            self._graph.connect(name, re_groups[1])

            self._foreign_keys[(name, re_groups[1])] = (
                re_groups[0], re_groups[2]
            )

    def link(self, table_one: str, table_two: str) -> tuple:
        tup = (table_one, table_two)
        if tup in self._foreign_keys.keys():
            return self._foreign_keys[tup]

        reverse = tuple(reversed(tup))
        if reverse in self._foreign_keys.keys():
            return tuple(reversed(self._foreign_keys[reverse]))
