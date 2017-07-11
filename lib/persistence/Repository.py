# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 04.07.2017
:Status: dev
:Copyright: MIT License
"""

import lib as pct
from lib import Level
from .ResourceCollection import ResourceCollection as RC

from os.path import dirname, join, abspath

import sqlite3
from overload import overload
import re
import collections


class RepositoryException(Exception):
    pass


class Repository(object):
    """
    Database access layer representation. Exposes a simplistic CRUD API and
    performs underlying SQL queries.

    To avoid expensive I/O operations, this class delays sql commits for an
    arbitrary amount of queries. This arbitrary amount can be changed through
    **Repository.commit_delay**.

    This class metaclass is Singleton. As such, any object creation subsequent
    to the first constructor call will not have any effect.

    .. seealso:: Singleton
    """
# ------------------------------------------------------------------- VARIABLES

    ForeignKey = collections.namedtuple("ForeignKey", [
        "from_table", "from_column", "dest_table", "dest_column"
    ])

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
        self.foreign_keys = list()
        self._foreign_keys()

        self.long_transaction = False

    def __del__(self) -> None:
        """
        Class destructor. Commits remaining queries and close the connection.
        """
        self.db_conn.commit()
        self.db_conn.close()

    def __getitem__(self, key: str) -> object:  # repo["data@experiments:69"], # repo["data@subjects:12"]
        composition = key.split("@")

        if len(composition) > 2:
            raise RepositoryException(
                "Composed queries do not support " +
                "multiple links"
            )
        # Linear query
        if len(composition) < 2:
            print(str(composition))
            request = composition[0].split(":")
            if len(request) < 2:
                return self._read(request[0])
            return self._read({'id': request[1]}, request[0])

        # Composed query
        if ":" in composition[0]:
            raise RepositoryException(
                "ID specified on left operand for linked query"
            )

        destination = composition[1].split(":")
        path = self._resolve(composition[0], destination[0])
        print(str(path))
        step_data = None

        for index, step in enumerate(reversed(path)):

            if step_data is None:
                step_data = self._read({
                    step.from_column: destination[1]
                }, step.from_table)
                continue

            tmp = list()
            for step_cell in step_data:
                tmp.extend(self._read({
                    step.from_column: step_cell[step.dest_column]
                }, step.from_table))
            step_data = tmp

        return step_data

    def __setitem__(self, key: str, value: dict) -> None:
        target = key.split(":")
        if len(target) > 2:
            raise IndexError("Illformed table[:id] request.")
        if len(target) == 2:
            if self.read({'id': target[1]}, target[0]):
                self.update(value, {'id': target[1]}, target[0])
                return
            raise IndexError("ID %s does not exist in database." % target[1])
        self.create(value, key)

    def __delitem__(self, key: str) -> None:
        pass

# --------------------------------------------------------------------- METHODS

    def _foreign_keys(self):
        """
        TODO
        """
        schema_query = """SELECT sql FROM (
            SELECT sql sql, type type, tbl_name tbl_name, name name
                FROM sqlite_master
                UNION ALL
            SELECT sql, type, tbl_name, name
                FROM sqlite_temp_master
        ) WHERE type != 'meta' AND sql NOTNULL AND name NOT LIKE 'sqlite_%'
        ORDER BY substr(type, 2, 1), name ;"""

        cursor = self.db_conn.execute(schema_query)

        table_strings = list()
        foreign_keys_strings = list()

        for result in cursor.fetchall():
            query = dict(result)["sql"]
            table_string = ""
            foreign_keys_string = list()
            for line in query.splitlines():
                if re.match(".*CREATE TABLE", line):
                    table_string = line
                if re.match(".*FOREIGN KEY", line):
                    foreign_keys_string.append(line)
            if table_string and foreign_keys_string:
                table_strings.append(table_string)
                foreign_keys_strings.append(foreign_keys_string)

        table_pattern = ".*CREATE TABLE (.*)"
        fk_pattern = ".*FOREIGN KEY \((.*)\) REFERENCES (.*) \((.*)\).*"
        for index in range(len(table_strings)):
            table_groups = [
                cell.strip(" ()\´`") for cell in list(
                    re.match(table_pattern, table_strings[index]).groups()
                )]
            for fk_string in foreign_keys_strings[index]:
                fk_groups = [
                    cell.strip(" ()\´`") for cell in list(
                        re.match(fk_pattern, fk_string).groups()
                    )]
                self.foreign_keys.append(Repository.ForeignKey(
                    table_groups[0], fk_groups[0], fk_groups[1], fk_groups[2]
                ))

    def _resolve(self, from_table: str, dest_table: str,
                 keys: list = None) -> ForeignKey:
        """
        TODO - DOCUMENTATION & INTERMEDIATE TABLES COMPATIBILITY
        """
        keys = self.foreign_keys if keys is None else keys

        for fk in keys:
            if fk.from_table == from_table and fk.dest_table == dest_table:
                return [fk]

        potent = False
        for key in keys:
            if key.dest_table == dest_table:
                potent = True
                break
        if not potent:
            return

        path = list()
        stack = list()
        stack.append([fk for fk in keys if fk.from_table == from_table])
        consumed = list()

        while stack:
            for fk in list(stack[-1]):
                path.append(fk)
                consumed.append(fk)

                if len(stack) < len(path):
                    path.pop()

                if path[-1] is not fk:
                    path[-1] = fk

                if fk.dest_table == dest_table:
                    stack = None
                    break

                candidates = [key for key in keys
                              if key not in consumed
                              and key.from_table == fk.dest_table]
                if candidates:
                    stack.append(candidates)
                    break

                stack[-1].remove(fk)
                if not stack[-1]:
                    stack.pop()
                    path.pop()

        return path

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

        pct.log("Building foreign key relations...")
        self.foreign_keys = list()
        self._foreign_keys()

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
        Use this before any read / update operation.
        """
        if not self.long_transaction:
            if self._transaction_count > 0:
                self.db_conn.commit()
                self._transaction_count = 0

    @overload
    def _read(self, constraints: dict, table: str) -> list:
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
        cpt = 0
        for key in constraints:
            if cpt > 0 and cpt < len(constraints):
                query_constraints += " AND "
            query_constraints += "{0}='{1}'".format(key, constraints[key])
            cpt += 1
        query = "SELECT * FROM {0} WHERE {1};".format(table, query_constraints)
        pct.log("Executing query : %s" % query, pct.Level.DEBUG)
        cursor = self.db_conn.execute(query)

        return [dict(cell) for cell in cursor.fetchall()]

    @_read.add
    def _read(self, table: str) -> list:
        """
        Pulls every records from the **table** table.
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

    def start_transaction(self):
        self._transaction_count = 0
        self.db_conn.commit()
        self.long_transaction = True

    def end_transaction(self):
        self.db_conn.commit()
        self.long_transaction = False

# ------------------------------------------------------------------ PROPERTIES

    @property
    def tables(self) -> list:
        cursor = self.db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )

        return [item for sublist in cursor.fetchall() for item in sublist]
