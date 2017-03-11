# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Last update: 11/03/2017
"""

import csv

class Datasheet(object):
    """
    Represents a - more elaborated - csv file.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, source=None, fieldnames=None, csv_list=None, delimiter=";"):
        self._source = source
        self._fieldnames = fieldnames
        self._delimiter = delimiter
        self._size = 0
        self._altered = False

        if csv_list is not None:
            self._csv = csv_list
        elif source is not None:
            self.open(source)

    def __str__(self):
        return("Datasheet holds {0} elements from {1}".format(
            str(self._size),
            (self._source if self._source is not None else "memory")
            ))

# ----------------------------------------------------------------------------------------- METHODS
    def open(self, source):
        """
        Opens the given file and fills this Datasheet with the content of the file.
        """
        self._source = source
        with open(source, "r") as fin:
            reader = csv.DictReader(fin, fieldnames=self._fieldnames, delimiter=self._delimiter)
            self._csv = list(reader)
            self._fieldnames = reader.fieldnames
        self._size = len(self._csv)

    def save(self, destination):
        """
        Writes the current datasheet state to a file.
        """
        with open(destination, "w") as fout:
            writer = csv.DictWriter(fout, self._fieldnames, delimiter=self._delimiter)
            writer.writeheader()
            for row in self._csv:
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

    def records(self):
        """
        records generator
        """
        for record in self._csv:
            yield record

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
                row[field] = self._csv[index][field]
            copy.append(row)
        return copy


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
