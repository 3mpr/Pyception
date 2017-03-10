# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import csv

class Datasheet(object):
    """
    Represents a - more elaborated - csv file.
    """

    def __init__(self, source_file_path, fieldnames, delimiter=";"):
        self._source_file_path = source_file_path
        self._fieldnames = fieldnames
        self._delimiter = delimiter
        with open(source_file_path, "r") as fin:
            reader = csv.DictReader(fin, fieldnames, delimiter=delimiter)
            self._source_csv = list(reader)
            self._dest_csv = self._source_csv
        self._nb_records = len(self._source_csv)

    def __str__(self):
        return("Datasheet holds {0} elements from {1}".format(
            str(self._nb_records),
            str(self._source_file_path)
            ))

    def dump(self, dest_file_path, fieldnames=None):
        """
        Writes the current datasheet state to a file.
        """
        fieldnames = self._fieldnames if fieldnames is None else fieldnames
        with open(dest_file_path, "w") as fout:
            writer = csv.DictWriter(fout, fieldnames, delimiter=self._delimiter)
            writer.writeheader()
            for row in self._dest_csv:
                to_write = {}
                for fieldname in fieldnames:
                    to_write[fieldname] = row[fieldname]
                writer.writerow(to_write)

    def remove_field(self, field):
        """
        Removes a column from this object destination file.
        """
        if field in self._fieldnames:
            self._fieldnames.remove(field)

    def fieldnames(self, fieldnames=None):
        """
        fieldnames mutator
        """
        if fieldnames is None:
            return self._fieldnames
        else:
            self._fieldnames = fieldnames

    def nb_records(self):
        """
        nb_records mutator
        """
        return self._nb_records

    def records(self):
        """
        records generator
        """
        for record in self._dest_csv:
            yield record
