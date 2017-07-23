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


class DBObject(object):
    """
    Object relationnal mapping of a database table schema. DBObject objects
    should not be instanciated, as they don't belong themselve to any mapping.
    Rather, runtime DBFactory types inheriting this implementation are the aim
    of this class method and properties. This class thus describes table
    independant logic and behaviours (e.g id, async loading, ...).

    :seealso: DBFactory
    """
# ------------------------------------------------------------------- VARIABLES

# ----------------------------------------------------------------------- MAGIC

    def __init__(self, table: str) -> None:
        self._table = table
        self._loaded = False

# --------------------------------------------------------------------- METHODS

    def _async__init__(self, **kwargs) -> None:
        for key, value in kwargs.items():

            if key == "id":
                continue

            if key not in self._attributes:
                raise TypeError("Argument %s not valid for %s" % (
                    key, self.__class__.__name__)
                )

            if self._check_links(key):
                print(key)
                cls = self._repository.safe.table_class(key)
                print(cls)
                object.__setattr__(
                    self, key, self._repository.safe.table_class(key)(value)
                )
                continue

            object.__setattr__(self, key, value)

    def _check_links(self, key: str) -> bool:
        fks = self._repository.schema.foreign_keys(self._table)
        for fk in fks:
            if fk[0] == key:
                return True
        return False

    def _load(self):
        self._loaded = True
        self._async__init__(
            **self._repository.read({'id': self._id}, self._table)[0]
        )

    def __getattribute__(self, attr) -> object:
        if not object.__getattribute__(self, '_loaded'):
            object.__getattribute__(self, '_async__init__')(
                **object.__getattribute__(self, '_repository').read({
                    'id': self._id
                }, self._table)[0]
            )
        return object.__getattribute__(self, attr)

    def update(self) -> None:
        """
        Updates this object states in the database definitely.
        """
        new_values = dict()
        for key in self._attributes:
            new_values[key] = getattr(self, key)
        self.repository.update({'id': self._id}, new_values, self._table)

# ------------------------------------------------------------------ PROPERTIES

    @property
    def id(self) -> int:
        return object.__getattribute__(self, "_id")


def DBFactory(table: str, repo, attrs: list) -> type:
    """
    Generates **DBObject** inherited class at runtime. This function is to be
    used with DBSchema information.

    :param table:       The table represented by the created type
    :param repo:        The repository of the database
    :param attrs:       The new object attributes which also happen to be the
                        aimed table columns
    :type table:        str
    :type repo:         Repository
    :type attrs:        list
    :return:            The new type
    :rtype:             type
    """
    def __init__(self, id):
        setattr(self, "_id", id)
        DBObject.__init__(self, table)

    new_class = type(table, (DBObject,), {'__init__': __init__})
    new_class._attributes = attrs
    new_class._repository = repo

    return new_class
