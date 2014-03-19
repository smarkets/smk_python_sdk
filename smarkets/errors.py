from __future__ import absolute_import, division, print_function, unicode_literals

import sys as _sys
from collections import namedtuple as _namedtuple
from contextlib import contextmanager as _contextmanager

import decorator as _decorator
import six as _six


def reraise(exception):
    prev_cls, prev, tb = _sys.exc_info()
    _six.reraise(type(exception), exception, tb)


@_contextmanager
def _swallow_manager(exceptions):
    try:
        yield
    except BaseException as e:
        if not isinstance(e, exceptions):
            raise


def swallow(exceptions, default=None):
    '''
    Swallow exception(s) when executing something. Works as function decorator and
    as a context manager:

    >>> @swallow(NameError, default=2)
    ... def fun():
    ...     a = b  # noqa
    ...     return 1
    ...
    >>> fun()
    2
    >>> with swallow(KeyError):
    ...    raise KeyError('key')
    ...

    :type exceptions: iterable of Exception or Exception
    :param default: value to return in case of an exception
    '''
    if isinstance(exceptions, type):
        exceptions = (exceptions,)
    else:
        exceptions = tuple(exceptions)

    return _SwallowHandler(exceptions, default)


class _SwallowHandler(_namedtuple('_SwallowHandlerBase', 'exceptions default')):

    def __call__(self, something):
        @_decorator.decorator
        def _swallow_decorator(f, *args, **kwargs):
            try:
                value = f(*args, **kwargs)
            except BaseException as e:
                if isinstance(e, self.exceptions):
                    value = self.default
                else:
                    raise

            return value

        return _swallow_decorator(something)

    def __enter__(self):
        pass

    def __exit__(self, type_, value, tb):
        return isinstance(value, self.exceptions)


class Error(Exception):

    "Base class for every Smarkets error"
