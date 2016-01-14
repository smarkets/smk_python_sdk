# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from six.moves import xrange  # noqa # used in doctest


class LazyCall(object):

    """Encapsulates a computation with defined arguments.

    Its main use case at the moment is to pass some relatively expensive to generate content
    to logging subsystem and not do the computations unless the variable is actually used,
    for example:

        log.debug('Received message %s', LazyCall(expensive_message_to_string, message))

    General behaviour:

        >>> counter = [0]
        >>> def computation(*args, **kwargs):
        ...     print('call!', args, kwargs)
        ...     counter[0] += 1
        ...     return 'result value'
        >>>
        >>> # str() convertion for the output below to not have
        >>> # the "u" prefix on Python 2 which makes this doctest
        >>> # Python 2 and Python 3 compatible.
        >>> result = LazyCall(computation, 1, 2, a=str('b'))
        >>> for i in xrange(3):
        ...     print(result.get_value())
        call! (1, 2) {'a': 'b'}
        result value
        result value
        result value
        >>> print(result)
        result value
        >>> print(counter[0])
        1
    """

    __slots__ = ('_callable', '_args', '_kwargs', '_value', '_has_value')

    def __init__(self, callable_, *args, **kwargs):
        self._callable = callable_
        self._args = args
        self._kwargs = kwargs
        self._value = None
        self._has_value = False

    def get_value(self):
        """Get the value of the computation. Computation is only executed once. """
        if not self._has_value:
            self._value = self._callable(*self._args, **self._kwargs)
            self._has_value = True

        return self._value

    def __str__(self):
        return str(self.get_value())

    def __unicode__(self):
        return str(self.get_value()).decode()
