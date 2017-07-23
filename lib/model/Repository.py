# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 21.07.2017
:Revision: 6
:Status: dev
:Copyright: MIT License
"""

import lib as pct
from lib import Level
from .ResourceCollection import ResourceCollection as RC
from .DBSchema import DBSchema
from .Safe import Safe

from os.path import dirname, join, abspath

import sqlite3
from overload import overload


class RepositoryException(Exception):
    pass


class Repository(object):
    """
    Database access layer representation. Exposes a simplistic CRUD API and
    performs underlying SQL queries.

    To avoid expensive I/O operations, this class delays sql commits for an
    arbitrary amount of queries. This arbitrary amount can be changed through
    **Repository.commit_delay**.
    """
# ------------------------------------------------------------------- VARIABLES

    db_conn = None

    _transaction_count = 0
    commit_delay = 50

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, db_file: str, schema_dir: str = join(
        dirname(abspath(__file__)), "sql")
    ) -> None:
        """
        Initializes the database connection and the sql schema directory.

        :param db_file:     The database file path.
        :type db_file:      str
        :param schema_dir:  The tables schema directory.
        :type schema_dir:   str
        """
        self.db_file = db_file
        self.db_conn = sqlite3.connect(db_file)
        self.db_conn.row_factory = sqlite3.Row

        self.schemas = RC(schema_dir, [".sql"])
        self.schema = DBSchema(self.db_conn)
        self.safe = Safe(self)

        self.long_transaction = False

    def __del__(self) -> None:
        """
        Class destructor. Commits remaining queries and close the connection.
        """
        self.db_conn.commit()
        self.db_conn.close()

# --------------------------------------------------------------------- METHODS

    def initialize(self) -> None:
        """
        Sets up the database schemas as specified in the schema_dir sql files.
        """
        pct.log("Initializing database %s..." % self.db_file,
                Level.INFORMATION)
        for fin in self.schemas.list():
            with open(fin, "r") as schema:
                query = schema.read().strip("\n")
                pct.log("Issuing SQL query:", Level.DEBUG)
                pct.log(query, Level.DEBUG)
                self.db_conn.execute(query)
        self.db_conn.commit()
        pct.log("Database initialized.", Level.INFORMATION)

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
    def create(self, values: dict, table: str) -> int:
        """
        Forges an INSERT query targeting the specified table from the given
        dictionary. This method will not check for sql consistency. As such;
        specified columns and values MUST respect the table schema.

        :param values:  The key / value dictionary where the key is a table
                        column and the value its value.
        :type values:   dict
        :param table:   The targeted table.
        :type table:    str
        :return:        The newly inserted row id (primary key)
        :rtype:         int
        """
        query_labels = ""
        query_keys = ""
        query_values = list()
        cpt = 0
        for key in values:
            if cpt > 0 and cpt < len(values):
                query_labels += ", "
                query_keys += ", "
            query_labels += key
            query_keys += "?"
            query_values.append(values[key])
            cpt += 1

        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(
            table, query_labels, query_keys
        )

        cursor = self.db_conn.execute(query, query_values)

        self._commit()
        return cursor.lastrowid

    @create.add
    def create(self, array: list, table: str) -> int:
        """
        Operates a serie of row creations as specified in this method original
        definition from the given dict array.

        :param array:   The list of key / values.
        :type array:    list
        :return:        The last inserted row id (primary key)
        :rtype:         int
        """
        lastrowid = -1
        for row in array:
            lastrowid = self.create(row, table)
        return lastrowid

    def _read_guard(self) -> None:
        """
        Commits uncommited queries and sets the transaction count to zero.
        Use this before any read / update operation. This method does not have
        any effect if a transaction has been started.

        :seealso: start_transaction
        """
        if not self.long_transaction:
            if self._transaction_count > 0:
                self.db_conn.commit()
                self._transaction_count = 0

    @overload
    def read(self, constraints: dict, table: str, lazy: bool = False) -> list:
        """
        Pulls the records corresponding to the **constraints** dictionnary from
        the **table** table.

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
        tgc = "id" if lazy else "*"

        for index, key in enumerate(constraints):
            if index > 0 and index < len(constraints):
                query_constraints += " AND "
            query_constraints += "{0}='{1}'".format(key, constraints[key])

        query = "SELECT {0} FROM {1} WHERE {2};".format(
            tgc, table, query_constraints
        )

        pct.log("Executing query : %s" % query, pct.Level.DEBUG)
        cursor = self.db_conn.execute(query)

        return [dict(cell) for cell in cursor.fetchall()]

    @read.add
    def read(self, constraints: dict, table: str, link: str,
             lazy: bool = False) -> list:
        """
        Attemps to find the connection between **table** and **link**
        from the underlying DBSchema before to match the **constraints**
        dictionnary on **table**. Records from **link** connected to the        tgc = "id" if lazy else "*"

        found **table** records are then returned.

        :param constraints: Key/value dictionnary used to filter the database
                            selection. Set to empty {} to pull the whole table
                            content.
        :param table:       The filtered table name.
        :param link:        The target data table which records are matched
                            against the selection.
        :type constraints:  dict
        :type table:        str
        :type link:         str
        :return:            A list of dictionnary, corresponding to the
                            records.
        :rtype:             list
        """
        self._read_guard()

        tgc = "id" if lazy else "*"
        path = self.schema.path(table, link)
        query_constraints = ""

        if not path:
            raise RepositoryException(
                "No connection found between {0} and {1}".format(table, link)
            )

        for index, key in enumerate(constraints):
            if index > 0 and index < len(constraints):
                query_constraints += " AND "
            query_constraints += "{2}.{0}='{1}'".format(
                key, constraints[key], table
            )

        query_join = ""
        for milestone in list(reversed(path.keys())):
            query_join += " INNER JOIN {0} ON {1}.{2}={3}.{4}".format(
                milestone[0], milestone[0], path[milestone][0],
                milestone[1], path[milestone][1]
            )

        query = "SELECT {1}.{0} FROM {1}{2} WHERE {3};".format(
            tgc, link, query_join, query_constraints
        )

        pct.log("Executing query : %s" % query, pct.Level.DEBUG)
        cursor = self.db_conn.execute(query)

        return [dict(cell) for cell in cursor.fetchall()]

    @read.add
    def read(self, table: str, lazy: bool = False) -> list:
        """
        Pulls every records from the **table** table.
        Same as `read({}, "table")`.

        :param table:   The table name.
        :type table:    str
        :return:        A list of dictionnaries, corresponding to the records.
        :rtype:         list
        """
        tgc = "id" if lazy else "*"
        self._read_guard()

        cursor = self.db_conn.execute("SELECT {0} FROM {1};".format(
            tgc, table
        ))

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

        query = "SELECT COUNT( * ) AS count FROM {0}".format(table)
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
            "SELECT COUNT( * ) AS count FROM {0};".format(table)
        )

        return dict(cursor.fetchone())['count']

    def _commit(self) -> None:
        """
        Increments the internal transaction count and checks whether it is time
        or not to commit the transactions to the database.
        """
        if not self.long_transaction:
            self._transaction_count += 1
            if self._transaction_count > self.commit_delay:
                self.db_conn.commit()
                self._transaction_count = 0

    def start_transaction(self) -> None:
        """
        Disables commits for un undetermined period of time. Useful to enhance
        performances in view of extended amount of queries.

        Call **end_transaction** to terminate.
        """
        self._transaction_count = 0
        self.db_conn.commit()
        self.long_transaction = True

    def end_transaction(self) -> None:
        """
        Returns to default Repository behaviour, commiting queries after
        **commit_delay**.
        """
        self.db_conn.commit()
        self.long_transaction = False

# ------------------------------------------------------------------ PROPERTIES
