"""Helper classes and exceptions
"""
# To enable postponed evaluation of annotations (default for 3.10)
from __future__ import annotations

from collections import OrderedDict
from enum import Enum
from typing import Union, List, Iterator

import pytz
import datetime as dt

__author__ = 'arwi'

TZ = pytz.timezone("Europe/Oslo")


Ordered = Union[dt.date, int]
OrderedElements = Union['Container', 'Day']


class Container:
    def __init__(self):
        self._elems: OrderedDict[Ordered, OrderedElements] = OrderedDict()

    def assimilate(self, other: Container) -> Container:
        container = type(self)()
        container._elems = OrderedDict(self._elems)
        for key, elem in container._elems.items():
            if key in other._elems:
                container[key] = elem.assimilate(other[key])
        for key, elem in other._elems.items():
            if key not in container:
                container[key] = elem
        return container._sort()._filter_empty()

    def _sort(self) -> Container:
        keys = sorted(self._elems.keys())
        for key in keys:
            self._elems.move_to_end(key)
        return self

    def _filter_empty(self) -> Container:
        for key in list(self._elems.keys()):
            if not key:
                del self._elems[key]
        return self

    def __getitem__(self, key: Union[Ordered, slice, List[Ordered]]) -> OrderedElements:
        if not isinstance(key, slice) and not isinstance(key, list):
            return self._elems[key]
        elif isinstance(key, list):
            new_container = type(self)()
            new_container._elems = OrderedDict({k: self._elems[k] for k in key if k in self._elems})
            return new_container
        elif isinstance(key, slice):
            if key.step != 1 and key.step is not None:
                raise ValueError("step value can only be 1")
            new_container = type(self)()
            for k, v in self._elems.items():
                if all([key.start, key.stop]) and key.start <= k < key.stop \
                        or key.start and not key.stop and key.start <= k \
                        or key.stop and not key.start and k < key.stop:
                    new_container[k] = v
            return new_container._sort()._filter_empty()

    def __setitem__(self, key: Ordered, elem: OrderedElements) -> None:
        self._elems[key] = elem

    def __iter__(self) -> Iterator[Container]:
        return iter(self._elems.values())

    def __contains__(self, key: Ordered) -> bool:
        return key in self._elems

    def __len__(self) -> int:
        return len(self._elems)

    def __bool__(self) -> bool:
        return bool(self._elems)


class FloatEnum(float, Enum):
    """Enum where members are also (and must be) floats. (Copied from Enum source.)"""

    def __str__(self):
        return "%s" % (self._name_,)

    def __format__(self, format_spec):
        """Returns format using actual value unless __str__ has been overridden."""
        str_overridden = type(self).__str__ != FloatEnum.__str__
        if str_overridden:
            cls = str
            val = str(self)
        else:
            cls = self._member_type_
            val = self._value_
        return cls.__format__(val, format_spec)


class RegobsError(Exception):
    pass


class NotAuthenticatedError(RegobsError):
    pass


class NoObservationError(RegobsError):
    pass


class AuthError(RegobsError):
    pass


class ApiError(RegobsError):
    pass
