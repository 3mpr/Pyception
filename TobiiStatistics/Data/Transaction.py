# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 14.03.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 22.03.2017
"""

import csv
import os.path
import re

from Perception.Design.Visited import Visited
from Perception.Design.VisitorInterface import VisitorInterface


class Transaction(Visited):
    """
    In-memory representation of a CSV file.
    """
# ------------------------------------------------------------------------------------------- MAGIC

    def __init__(self, table, headers, delimiter=";"):
        """
        :param table: List<Dict>
        :param headers: Dict
        :param delimiter: char
        :rtype: Transaction
        """
        self._table = table
        self._headers = headers
        self._delimiter = delimiter

        self._adapted = False
        self._bound = False
        self._file = None

    def __iter__(self):
        return iter(self._table)

    def __getitem__(self, key):
        return self._table[key]

    def __setitem__(self, key, value):
        self._table[key] = value

    def __delitem__(self, key):
        del self._table[key]

    def __eq__(self, other):
        if self.count() != other.count():
            return False

        if self._headers != other.headers():
            return False

        for index in range(0, self.count() - 1):
            for header in self._headers:
                if self._table[index][header] != other[index][header]:
                    return False

        return True

    def __div__(self, visitor):
        assert(isinstance(visitor, VisitorInterface),
            "Expected a visitor, received {0}:{1}".format(visitor, type(visitor))
        )
        return self.accept(visitor)

# ----------------------------------------------------------------------------------------- METHODS

    @staticmethod
    def open(file_path, headers=None, delimiter=";"):
        """
        Tiny object factory that opens a CSV file and returns a Paper.
        The returned paper is bound to the specified file.

        :param file_path: string
        :param headers: List
        :param delimiter: char
        :rtype: Transaction
        """
        with open(file_path, "r") as fin:
            reader = csv.DictReader(fin, headers, delimiter=delimiter)
            table = list(reader)
            paper = Transaction(table, reader.fieldnames, delimiter)
        paper.bind(file_path, True)
        return paper

    def save(self, destination=None):
        """
        Save this Transaction as a CSV file to the given destination.
        Does NOT check or attempt to create intermediate directories.

        :param destination: string
        :rtype: void
        """
        if destination is None and not self._bound:
            raise IOError("Transaction save requester but paper is not linked to any source.")

        destination = self._file if destination is None else destination

        with open(destination, "w") as fout:
            writer = csv.DictWriter(fout, self._headers, delimiter=self._delimiter)
            writer.writeheader()
            for row in self._table:
                to_write = {}
                for header in self._headers:
                    to_write[header] = row[header]
                writer.writerows(to_write)

    def bind(self, source, verify=True, overwrite=False):
        """
        Bind this Transaction to a the given file source.
        Does check for path existence and source to internal table correlation.
        If overwrite is set to true, the correlation is not verified.

        :param source: string
        :param verify: boolean
        :param overwrite: boolean
        """
        if not os.path.exists(source):
            raise IOError("Requested bind to %s but path does not exist." % source)

        if verify:
            paper = Transaction.open(source)
            if not paper == self and not overwrite:
                raise AssertionError(
                    "Requested bind to %s but in-memory paper and source paper are not equals."
                    % source
                )

        self._file = source
        self._bound = True

    def unbind(self):
        """
        Unbind this paper from its source and returns.

        :return: string
        """
        source = self._file
        self._file = None
        self._bound = False
        return source

    def add(self, header):
        """
        Adds a header to this Transaction headers.

        :param header: string
        :rtype: void
        """
        self._headers.append(header)
        self._adapted = True

    def remove(self, header):
        """
        Removes a header from this Transaction headers.
        Returns true if the header was in this Transaction headers, false otherwise.

        :param header: string
        :rtype: bool
        """
        if header in self._headers:
            self._headers.remove(header)
            self._adapted = True
            return True
        return False

    def count(self):
        """
        Counts the number of row in this Transaction.

        :return: int
        """
        return len(self._table)

    def match(self, pattern, header, begin=0, end=None):
        """
        Performs a regex match in this Transaction's given column.
        Returns the first found occurrence's index and regex match

        :return: int, re
        """
        end = self.count() - 1 if end is None else end
        for index in range(begin, end):
            cell = self._table[index][header]
            cell = "" if cell is None else cell
            match = pattern.match(cell)
            if match:
                return index, match

    def copy(self, begin=0, end=None, headers=None):
        """
        Copy this paper from the specified begin point to the specified end point.
        Both are respectively set to 0 and to this Transaction's end when omitted (full copy).

        :param begin: int
        :param end: int
        :param headers: Dict
        :return: Transaction
        """
        end = self.count() - 1 if end is None else end
        headers = self._headers if headers is None else headers

        if end > self.count() - 1:
            raise IndexError("Reached end of internal table range, unable to copy.")
        for header in headers:
            if header not in self._headers:
                raise IndexError(
                    "Header %s given in headers dictionary is not present in internal table headers, unable to copy"
                    % header
                )

        table = list()
        table_index = 0
        for index in range(begin, end):
            table.append({})
            for header in headers:
                table[table_index][header] = self._table[index][header]
            table_index += 1

        return Transaction(table, headers)

    def append(self, line):
        """
        Append an element to the end of this Transaction.

        :param line: dict
        """
        assert isinstance(line, dict), "row is not a dictionary: %s" % str(line)
        self._table[self.count()] = line
        self._adapted = True

    def prepend(self, line):
        """
        Prepend an element to the beginning of this Transaction.

        :param line: dict
        """
        assert isinstance(line, dict), "row is not a dictionary: %s" % str(line)
        self._table.insert(0, line)
        self._adapted = True

    def occurrence(self, var, field=None, expression=False):
        """
        Search for occurrences of the given variable in the internal table.

        :param var: string The searched value
        :param field: string The column to search in or None if the search has to be done in every column
        :param expression: bool Whether the given <var> is a regular expression.
        :return: list The index(es) of the rows where the value was found if any
        """
        def search_with_field(row, fieldname, var):
            return row[fieldname] == var

        def search_without_field(row, fieldname, var):
            return var in row

        def search_with_field_expr(row, fieldname, expr):
            return re.match(expr, row[fieldname])

        def search_without_field_expr(row, fieldname, expr):
            for cell in row:
                if re.match(expr, cell):
                    return True

        if field is None:
            search = search_without_field_expr if expression else search_without_field
        else:
            search = search_with_field_expr if expression else search_with_field

        occur = list()
        for index in range(self.count() - 1):
            if search(self._table[index], field, var):
                occur.append(index)

        return occur

# -------------------------------------------------------------------------------------- PROPERTIES

    @property
    def table(self):
        return self._table

    @property
    def headers(self, headers=None):
        if headers is None:
            return self._headers
        else:
            assert isinstance(headers, list), u"Expected list, received {}".format(type(headers))
            self._headers = headers
            self._adapted = True

    @property
    def delimiter(self, delimiter=None):
        if delimiter is None:
            return self._delimiter
        else:
            assert isinstance(delimiter, str), u"Expected string, received {}".format(type(delimiter))
            self._delimiter = delimiter
            self._adapted = True

    @property
    def adapted(self):
        return self._adapted

    @property
    def bound(self):
        return self._bound

    @property
    def bound_to(self):
        return self._file
