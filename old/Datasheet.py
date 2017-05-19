# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the Perception package
by Florian Indot <florian.indot@gmail.com>

Last update: 13/03/2017
"""

import csv

class Datasheet(object):
    """
    Represents a - more elaborated - csv file.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, source=None, fieldnames=None, table=None, delimiter=";"):
        self._source = source
        self._fieldnames = fieldnames
        self._delimiter = delimiter
        self._size = 0
        self._altered = False

        if table is not None:
            self._table = table
            self._size = len(self._table)
        elif source is not None:
            self.open(source)

    def __str__(self):
        return("Datasheet holds {0} elements from {1}".format(
            str(self._size),
            (self._source if self._source is not None else "memory")
            ))

    def __iter__(self):
        return iter(self._table)

    def __getitem__(self, key):
        return self._table[key]

# ----------------------------------------------------------------------------------------- METHODS
    def open(self, source):
        """
        Opens the given file and fills this Datasheet with the content of the file.
        """
        self._source = source
        with open(source, "r") as fin:
            reader = csv.DictReader(fin, fieldnames=self._fieldnames, delimiter=self._delimiter)
            self._table = list(reader)
            self._fieldnames = reader.fieldnames
        self._size = len(self._table)

    def save(self, destination):
        """
        Writes the current datasheet state to a file.
        """
        with open(destination, "w") as fout:
            writer = csv.DictWriter(fout, self._fieldnames, delimiter=self._delimiter)
            writer.writeheader()
            for row in self._table:
                to_write = {}
                for fieldname in self._fieldnames:
                    to_write[fieldname] = row[fieldname]
                writer.writerow(to_write)

    def add(self, field):
        """
        Adds a field to this object fields.
        """
        self._fieldnames.append(field)
        self._altered = True

    def remove(self, field):
        """
        Removes a column from this object destination file.
        """
        if field in self._fieldnames:
            self._fieldnames.remove(field)
        self._altered = True

    def count(self):
        """
        nb_records mutator
        """
        return self._size

    def copy(self, fieldnames=None, begin=0, end=None):
        """
        Copies a part of this csv or the whole csv if no
        arguments are provided.
        """
        fieldnames = self._fieldnames if fieldnames is None else fieldnames
        end = self._size if end is None else end
        copy = list()
        for index in range(begin, end):
            row = {}
            for field in fieldnames:
                row[field] = self._table[index][field]
            copy.append(row)
        return copy

    def seek(self, expression, field, begin=0):
        """
        Seeks from <begin> the given expression in the internal csv list.
        """
        for index in range(begin, self._size - 1):
            analyzed = (self._table[index][field]
                        if self._table[index][field] is not None
                        else "")
            match = expression.match(analyzed)
            if match:
                return index, match

        return False, False



# ---------------------------------------------------------------------------------------- MUTATORS
    def fieldnames(self, fieldnames=None):
        """
        fieldnames mutator.
        """
        if fieldnames is None:
            return self._fieldnames
        else:
            self._fieldnames = fieldnames

    def source(self):
        """
        source mutator.
        """
        return self._source

    def altered(self):
        """
        alteration mutator.
        """
        return self._altered

    def size(self):
        """
        Returns the number of row of this Datasheet.
        """
        return self._size
        