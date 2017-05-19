# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 22.03.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 22.03.2017
"""


class OrderedDict(object):
    def __init__(self, table, headers):
        self._table = list()
        self._headers = headers

        if len(table) is not len(headers):
            raise IndexError("Length of data table and header table mush be equal.")

        if type(table) is dict:
            for key in table:
                self._table.append(table[key])
        elif type(table) is tuple:
            for element in table:
                self._table.append(element)
        elif type(table) is list:
            self._table = table
        else:
            raise TypeError("OrderedDict object cannot be initialized from {}.".format(type(table)))

    def __getitem__(self, item):
        if type(item) is str:
            if item not in self._headers:
                raise IndexError("Element {} does not exist in OrderedDict.".format(item))
            return self._table[self._headers.index(item)]
        return self._table[item]

    def __setitem__(self, key, value):
        if type(key) is str:
            try:
                if self._headers.index(key) > len(self._table) - 1:
                    self._table.append(value)
                else:
                    self._table[self._headers.index(key)] = value
            except ValueError:
                self._headers.append(key)
                self._table.append(value)
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

    def index(self, header: str) -> int:
        return self.headers.index(header)

    @property
    def content(self):
        return self._table

    @property
    def headers(self):
        return self._headers
