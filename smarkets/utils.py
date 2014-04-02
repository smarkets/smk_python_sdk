from __future__ import absolute_import, division, print_function, unicode_literals

from time import time
from contextlib import contextmanager


class TimedResult(object):
    def get_value(self):
        """
        :return: Duration in miliseconds
        :rtype: float
        """
        try:
            return self._value
        except AttributeError:
            raise Exception('You can only get the value after exiting timing context')

    def _set_value(self, value):
        self._value = value


@contextmanager
def timed(time=time):
    start = time()
    result = TimedResult()
    yield result
    duration = (time() - start) * 1000.0
    result._set_value(duration)
