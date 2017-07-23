# -*- coding: utf-8 -*-

"""
Part of the **Pyception** package.

:Version: 1
:Authors: - Florian Indot
:Contact: florian.indot@gmail.com
:Date: 23.07.2017
:Revision: 1
:Copyright: MIT License
"""

from collections.abc import MutableSequence
from .DBObject import DBFactory

import inflection


class SafeException(Exception):
    pass


class Safe(MutableSequence):

    def __init__(self, repository) -> None:
        self._repository = repository

        for table in repository.schema.tables:
            classname = inflection.singularize(table).title()
            setattr(self, classname, DBFactory(
                table, repository, repository.schema.columns(table))
            )

    def __getitem__(self, request):
        composition = request.split("@")

        classname = inflection.singularize(composition[0]).title()
        cls = getattr(self, classname)

        if len(composition) < 2:
            return [cls(cell["id"]) for cell in self._repository.read(
                request, lazy=True
            )]

        target = composition[0]
        source = composition[1]

        request_filter = dict()

        try:
            source_comp = source.split(':')
            source = source_comp[0]
            request_filter['id'] = source_comp[1]
        except Exception as e:
            raise SafeException("Malformed composed request '%s'" % request)

        return [cls(cell["id"]) for cell in self._repository.read(
            request_filter, source, target, lazy=True
        )]

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __len__(self):
        pass

    def __contains__(self, key):
        pass

    def insert(self, val):
        pass

    def table_class(self, table_name):
        classname = inflection.singularize(table_name).title()
        return getattr(self, classname)
