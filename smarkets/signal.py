# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from copy import copy


class Signal(object):

    """
    All instance methods of this class are thread safe.
    """

    def __init__(self):
        self._handlers = set()

    def add(self, handler):
        """
        Add signal handler. You can also do::

            signal = Signal()
            signal += handler
        """
        self._handlers.add(handler)

        return self

    __iadd__ = add
    handle = add

    def remove(self, handler):
        """
        Remove signal handler. You can also do::

            signal = Signal()
            # add a handler "handler"
            signal -= handler
        """
        self._handlers.remove(handler)

        return self

    __isub__ = remove
    __unhandle__ = remove

    def fire(self, **kwargs):
        """Execute all handlers associated with this Signal.

        You can also call signal object to get the same result::

            signal = Signal()
            signal()  # calls the signal handler
        """
        for handler in copy(self._handlers):
            handler(**kwargs)

    __call__ = fire

    def __len__(self):
        return len(self._handlers)

    def __iter__(self):
        return iter(self._handlers)
