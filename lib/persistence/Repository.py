# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 12.06.2017
:Status: dev
:Copyright: MIT License
"""

from lib import pattern
from .ResourceCollection import ResourceCollection as RC
from lib import Transaction

from os.path import dirname, join, abspath

import sqlite3
from overload import overload
from pandas import DataFrame


class Repository(object):
    """
    Database access layer representation. Exposes a simplistic API and
    translate those calls into SQL queries.

    :todo: the doc & class completion
    """
# ------------------------------------------------------------------- VARIABLES

    __metaclass__ = pattern.Singleton

    db_conn = None
    sql_dir = join(dirname(abspath(__file__)), "sql")

    CRUD = {
        'create': RC(join(sql_dir, "create"), [".sql"]),
        'read': RC(join(sql_dir, "read"), [".sql"]),
        'update': RC(join(sql_dir, "update"), [".sql"]),
        'delete': RC(join(sql_dir, "delete"), [".sql"])
    }

    schemas = RC(join(sql_dir, "schemas"), [".sql"])

    cache = {
        'table': "",
        "query_args_len": 0,
        'query': ""
    }

    _transaction_count = 0
    commit_delay = 50

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, db_file):
        """
        Class constructor. Initializes the database connection.
        """
        self.db_conn = sqlite3.connect(db_file)
        self.db_conn.row_factory = sqlite3.Row

    def __del__(self):
        """
        Class destructor. Commit remaining queries and close the connection.
        """
        self.db_conn.commit()
        self.db_conn.close()

    def __len__(self):
        """
        Returns this database dataset length.
        """
        return self.count("data")

# --------------------------------------------------------------------- METHODS

    def initialize(self) -> None:
        """
        Sets up the database schemas.
        """
        for f in self.schemas.list():
            with open(f, "r") as schema:
                self.db_conn.execute(schema.read().strip("\n"))
        self.db_conn.commit()

    def drop(self, table: str = "") -> None:
        """
        Drop the table :table: and every records it contains.

        :param table: The table name, set to "" to drop every table.
        :type table: str

        .. warning:: The database content will be lost forever.
        """
        if table == "":
            for table in self.tables:
                self.db_conn.execute("DROP TABLE {0};".format(table))
        else:
            self.db_conn.execute("DROP TABLE {0};".format(table))
        self.db_conn.commit()

    @overload
    def create(self, row: list, table: str) -> int:
        """
        TODO CHANGE SIGNATURE
        """
        if table == self.cache["table"] \
           and len(row) == self.cache["query_args_len"]:
            cursor = self.db_conn.execute(self.cache["query"], *row)
        else:
            with open(self.CRUD["create"].get(table), "r") as fin:
                self.cache["query"] = fin.read().strip("\n")
            cursor = self.db_conn.execute(self.cache["query"], *row)

        self.cache["table"] = table
        self.cache["query_args_len"] = len(row)

        self._commit()
        return cursor.lastrowid

    @create.add
    def create(self, trs: Transaction, table: str) -> int:
        """
        TODO CHANGE  SIGNATURE AND SEE IF OVERLOAD IS NECESSARY
        """
        with open(self.CRUD["create"].get(table), "r") as fin:
            query = fin.read().strip("\n")
            for row in trs:
                cursor = self.db_conn.execute(query, [t for t in row.content])

        self._commit()
        return cursor.lastrowid

    def _read_guard(self) -> None:
        """
        Commits uncommited queries and sets the transaction count to zero.
        Use this before any read / update operation.
        """
        if self._transaction_count > 0:
            self.db_conn.commit()
            self._transaction_count = 0

    @overload
    def read(self, constraints: dict, table: str) -> list:
        """
        Pulls the records corresponding to the :constraints: dictionnary from
        the table :table:.

        :param constraints: Key/value dictionnary used to filter the database
                            selection. Set to empty {} to pull the whole table
                            content.
        :param table:       The table name.
        :type constraints:  dict
        :type table:        str
        :return:            A list of dictionnary, corresponding to the
                            records.
        :rtype:             list
        """
        self._read_guard()

        query_constraints = ""
        cpt = 0
        for key in constraints:
            if cpt > 0 and cpt < len(constraints):
                query_constraints += " AND "
            query_constraints += "{0}='{1}'".format(key, constraints[key])
            cpt += 1
        query = "SELECT * FROM {0} WHERE {1};".format(table, query_constraints)
        cursor = self.db_conn.execute(query)

        return [dict(cell) for cell in cursor.fetchall()]

    @read.add
    def read(self, table: str) -> list:
        """
        Pulls every records from the table :table:.
        Same as `read({}, "table")`.

        :param table:   The table name.
        :type table:    str
        :return:        A list of dictionnaries, corresponding to the records.
        :rtype:         list
        """
        self._read_guard()

        cursor = self.db_conn.execute("SELECT * FROM {0};".format(table))

        return [dict(cell) for cell in cursor.fetchall()]

    def update(self, updates: dict, constraints: dict, table: str,
               precommit: bool = True) -> None:
        """
        Updates the record(s) that meet the :constraints: constraints with the
        :updates: values.

        :param updates:     The key/value dataset that will replace the old(s)
                            dataset.
        :param constraints: Key/value dictionnary used to filter the database
                            selection. Set to empty {} to update the whole
                            table content.
        :param table:       The table name
        :param precommit:   Whether to commit before the update or not. Default
                            to true.
        :type updates:      dict
        :type constraints:  dict
        :type table:        str
        """
        if precommit:
            self._read_guard()

        query_constraints = ""
        cpt = 0
        for key in constraints:
            if cpt > 0 and cpt < len(constraints):
                query_constraints += " AND "
            query_constraints += "{0}='{1}'".format(key, constraints[key])
            cpt += 1

        cpt = 0
        query_updates = ""
        for key in updates:
            if cpt > 0 and cpt < len(updates):
                query_updates += ", "
            query_updates += "{0}='{1}'".format(key, updates[key])
            cpt += 1

        query = "UPDATE {0} SET {1} WHERE {2};".format(
            table,
            query_updates,
            query_constraints
        )
        self.db_conn.execute(query)

        self._commit()

    @overload
    def count(self, constraints: dict, table: str) -> int:
        """
        Counts the number of records in the :table: table that meet the
        :constraints: constraints.

        :param constraints: Key/value dictionnary used to filter the database
                            selection, reduces the final count. Set to empty {}
                            to get the total table count.
        :param table:       The table name.
        :type constraints:  dict
        :type table:        str
        :return:            The number of records.
        :rtype:             int
        """
        self._read_guard()

        query = "SELECT COUNT( id ) AS count FROM {0}".format(table)
        if constraints != {}:
            query_constraints = " WHERE "
            cpt = 0
            for key in constraints:
                if cpt > 0 and cpt < len(constraints):
                    query_constraints += " AND "
                query_constraints += "{0}='{1}'".format(key, constraints[key])
                cpt += 1
            query = query + query_constraints
        query += ";"
        cursor = self.db_conn.execute(query)

        return dict(cursor.fetchone())['count']

    @count.add
    def count(self, table: str) -> int:
        """
        Counts the number of records in the :table: table.
        Same as `count({}, "table")`.

        :param table:   The table name
        :type table:    str
        :return:        The number of records.
        :rtype:         int
        """
        cursor = self.db_conn.execute(
            "SELECT COUNT( id ) AS count FROM {0};".format(table)
        )

        return dict(cursor.fetchone())['count']

    def _commit(self) -> None:
        """
        Increments the internal transaction count and checks whether it is time
        or not to commit the transactions to the database.
        """
        self._transaction_count += 1
        if self._transaction_count > self.commit_delay:
            self.db_conn.commit()
            self._transaction_count = 0

    def columns(self, table: str) -> list:
        """
        Pull the column names of the :table: table.

        :param table:   The table name.
        :type table:    str
        :return:        The list of names
        :rtype:         list
        """
        cursor = self.db_conn.execute("SELECT * FROM {0}".format(table))
        return [description[0] for description in cursor.description]

# ------------------------------------------------------------------ PROPERTIES

    @property
    def tables(self) -> list:
        with open(self.CRUD["read"].get("tables"), "r") as fin:
            cursor = self.db_conn.execute(fin.read())
        return [item for sublist in cursor.fetchall() for item in sublist]
