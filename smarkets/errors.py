# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import decorator as _decorator
import sys as _sys
import six as _six


def reraise(exception):
    prev_cls, prev, tb = _sys.exc_info()
    _six.reraise(type(exception), exception, tb)


def swallow(exceptions, default=None):
    '''
    Swallow listed exceptions when executing decorated function.

    ::

        @swallow(NameError)
        def fun():
            a = b

        fun() # => None

    :type exceptions: tuple of Exception or Exception
    :param default: value to return in case of an exception
    '''
    if isinstance(exceptions, type):
        exceptions = [exceptions]

    @_decorator.decorator
    def swallow_decorator(f, *args, **kwargs):
        try:
            value = f(*args, **kwargs)
        except BaseException as e:
            if isinstance(e, tuple(exceptions)):
                value = default
            else:
                raise

        return value

    return swallow_decorator


class Error(Exception):

    "Base class for every Smarkets error"
