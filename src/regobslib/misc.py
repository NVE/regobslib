# -*- coding: utf-8 -*-
"""Helper classes and exceptions
"""

from enum import Enum
import pytz

__author__ = 'arwi'

TZ = pytz.timezone("Europe/Oslo")


class FloatEnum(float, Enum):
    """
    Enum where members are also (and must be) floats
    """

    def __str__(self):
        return "%s" % (self._name_,)

    def __format__(self, format_spec):
        """
        Returns format using actual value unless __str__ has been overridden.
        """
        str_overridden = type(self).__str__ != FloatEnum.__str__
        if str_overridden:
            cls = str
            val = str(self)
        else:
            cls = self._member_type_
            val = self._value_
        return cls.__format__(val, format_spec)


class Error(Exception):
    pass


class NotAuthenticatedError(Error):
    pass


class NoObservationError(Error):
    pass


class AuthError(Error):
    pass


class ApiError(Error):
    pass


class SpatialError(Error):
    pass


class ElevationError(Error):
    pass


class PercentError(Error):
    pass


class RangeError(Error):
    pass


class InvalidArgumentError(Error):
    pass
