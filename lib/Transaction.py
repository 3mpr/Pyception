# -*- coding: utf-8 -*-

"""
Part of the **PyCeption** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 13.06.2017
:Revision: 10
:Copyright: MIT License
"""

import csv
import os.path
import io
import re
import random

from .pattern.Visited import Visited
from .pattern.VisitorInterface import VisitorInterface


class Transaction(Visited):
    """
    All purpose data structure. Stands as a set of tool for manipulating
    data, it can be extanded through the use of visitors.

    :see: Visited
    :see: Visitor
    """

    class Row(object):
        """
        Transaction row definition. Implemented as both an index and
        associative accessible array.
        """
        def __init__(self, table, headers):
            self._table = list()
            self._headers = headers
            if type(table) is dict:
                for key in table:
                    self._table.append(table[key])
            elif type(table) is tuple:
                for element in table:
                    self._table.append(element)
            elif type(table) is list:
                self._table = table
            else:
                raise TypeError("Row object cannot be initialized from {}.".
                                format(type(table)))

        def __getitem__(self, item):
            if type(item) is str:
                if item not in self._headers:
                    raise IndexError(
                        "Element {0} does not exist in row.\nRow : {1}\nHeaders:".format(item, str(self), str(self.headers)))
                return self._table[self._headers.index(item)]
            return self._table[item]

        def __setitem__(self, key, value):
            if type(key) is str:
                if self._headers.index(key) > len(self._table) - 1:
                    self._table.append(value)
                else:
                    self._table[self._headers.index(key)] = value
            else:
                self._table[key] = value

        def __delitem__(self, key):
            if type(key) is str:
                del self._table[self._headers.index(key)]
            else:
                del self._table[key]

        def __str__(self):
            return str(self._table)

        def __iter__(self):
            return iter(self._table)

        def __len__(self):
            return len(self._table)

        @property
        def content(self):
            return self._table

        @property
        def headers(self):
            return self._headers

# ------------------------------------------------------------------------------------------- MAGIC

    def __init__(self, table, headers):
        """
        :param table: List<Dict>
        :param headers: Dict
        :param delimiter: char
        :rtype: Transaction
        """
        self._table = list()

        for row in table:
            for cell in row:
                if row == "":
                    continue
            self._table.append(Transaction.Row(row, headers))

        self._headers = headers

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
        for index in range(key, self.count() - 1):
            self._table[key] = self._table[key + 1]

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
        assert isinstance(visitor, VisitorInterface), \
                "Expected a visitor, received {0}:{1}".format(
                    visitor, type(visitor)
                )
        return self.accept(visitor)

    def __len__(self):
        return len(self._table)

    def __iter__(self):
        return (x for x in self.table)

# ----------------------------------------------------------------------------------------- METHODS

    @staticmethod
    def open(file_path, headers=None, delimiter=";", enforce_policy=None):
        """
        Tiny object factory that opens a CSV file and returns a Transaction.
        The returned transaction is bound to the specified file.

        :param file_path: string
        :param headers: List
        :param delimiter: char
        :rtype: Transaction
        """
        with io.open(file_path, newline='\n') as fin:
            reader = csv.reader(fin, delimiter=delimiter)
            table = list(reader)
            if headers is None:
                headers = table[0]
            if table[0] == headers:
                table.pop(0)
            transaction = Transaction(table, headers)

        if enforce_policy is not None:
            validator = CSValidator(enforce_policy)
            validator.validate(transaction)

        transaction.bind(file_path, False)
        return transaction

    def save(self, destination=None, delimiter=";"):
        """
        Save this Transaction as a CSV file to the given destination.
        Does NOT check or attempt to create intermediate directories.

        :param destination: string
        :rtype: void
        """
        if destination is None and not self._bound:
            raise IOError(
                "Transaction save requested but transaction is not linked to any source."
            )

        destination = self._file if destination is None else destination

        with open(destination, "w") as fout:
            writer = csv.DictWriter(
                fout, self._headers, delimiter=delimiter)
            writer.writeheader()
            for row in self._table:
                to_write = {}
                for header in self._headers:
                    to_write[header] = row[header]
                writer.writerow(to_write)

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
            raise IOError(
                "Requested bind to %s but path does not exist." % source)

        if verify:
            transaction = Transaction.open(source)
            if not transaction == self and not overwrite:
                raise AssertionError(
                    "Requested bind to %s but in-memory transaction and source transaction are not equals."
                    % source)

        self._file = source
        self._bound = True

    def unbind(self):
        """
        Unbind this transaction from its source and returns.

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
            for row in self._table:
                del row[header]
            self._headers.remove(header)
            self._adapted = True
            return True
        return False

    def pop(self, row_id: int):
        self.table.pop(row_id)

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
        Copy this transaction from the specified begin point to the specified end point.
        Both are respectively set to 0 and to this Transaction's end when omitted (full copy).

        :param begin: int
        :param end: int
        :param headers: Dict
        :return: Transaction
        """
        end = self.count() - 1 if end is None else end
        headers = self._headers if headers is None else headers

        if end > self.count() - 1:
            raise IndexError(
                "Reached end of internal table range, unable to copy.")
        for header in headers:
            if header not in self._headers:
                raise IndexError(
                    "Header %s given in headers dictionary is not present in internal table headers, unable to copy"
                    % header)

        table = list()
        table_index = 0
        for index in range(begin, end):
            table.append(list())
            for header in headers:
                table[table_index].append(self._table[index][header])
            table_index += 1

        return Transaction(table, headers)

    def append(self, line):
        """
        Append an element to the end of this Transaction.

        :param line: dict
        """
        assert isinstance(line,
                          dict), "row is not a dictionary: %s" % str(line)
        headers = list()
        table = list()
        for key in line.keys():
            headers.append(key)
            table.append(line[key])
        self._table.append(Transaction.Row(table, headers))
        self._adapted = True

    def prepend(self, line):
        """
        Prepend an element to the beginning of this Transaction.

        :param line: dict
        """
        assert isinstance(line,
                          dict), "row is not a dictionary: %s" % str(line)
        headers = list()
        table = list()
        for key in line.keys():
            headers.append(key)
            table.append(line[key])
        self._table.insert(0, Transaction.Row(table, headers))
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

    def column(self, header):
        """
        Returns the column specified by 'header'.

        :param header: string The column's name
        :return The column
        :rtype list
        """
        if header not in self.headers:
            raise IndexError(
                "{} does not exist in internal table.".format(header))
        column = list()
        for index in range(len(self._table)):
            column.append(self._table[header])
        return column

    def mean(self, header=None):
        """
        Returns the mean (float) value of the given column.
        This method only works on columns holding integers, floats and doubles.
        It can and will raise errors on incorrect column types.

        :param header: string The column's name
        :return: The mean value
        :rtype float
        """
        if header is not None:
            return float(sum(self.column(header))) / float(len(self._table))

        mean = 0.0
        for row in self._table:
            mean += float(len(row.content))
        mean /= self.count()
        return round(mean)

    def sample(self):
        return list(self[random.randrange(0, self.count() - 1)])

    def index(self, element) -> int:
        # type: (Transaction.Row) -> int
        return self._table.index(element)

# -------------------------------------------------------------------------------------- PROPERTIES

    @property
    def table(self):
        return self._table

    @property
    def headers(self, headers=None):
        if headers is None:
            return self._headers
        else:
            assert isinstance(
                headers,
                list), u"Expected list, received {}".format(type(headers))
            self._headers = headers
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
