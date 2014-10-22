from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from itertools import chain

from mock import Mock, sentinel
from nose.tools import eq_, raises
from six.moves import xrange

from smarkets.signal import Signal


class SignalTest(unittest.TestCase):

    "Test the `smarkets.Callback` class"

    def setUp(self):
        "Set up the tests"
        self.callback = Signal()

    def tearDown(self):
        "Tear down the test requirements"
        self.callback = None

    def test_simple_fire(self):
        "Test the simple case where the handler fires"
        handler = Mock()
        self.callback += handler
        self.assertFalse(handler.called)
        self.assertEquals(1, len(self.callback))
        self.callback(message=sentinel.message)
        handler.assert_called_once_with(message=sentinel.message)
        self.assertEquals(1, len(self.callback))

    def test_unhandle(self):
        "Test the case where a handler is removed"
        handler = Mock()
        self.callback += handler
        self.assertFalse(handler.called)
        self.assertEquals(1, len(self.callback))
        self.callback -= handler
        self.assertEquals(0, len(self.callback))
        self.callback(message=sentinel.message)
        self.assertFalse(handler.called)

    def test_2_handlers(self):
        "Test 2 handlers both get called"
        handler1 = Mock()
        handler2 = Mock()
        self.callback += handler1
        self.callback += handler2
        self.assertFalse(handler1.called)
        self.assertFalse(handler2.called)
        self.assertEquals(2, len(self.callback))
        self.callback(message=sentinel.message)
        handler1.assert_called_once_with(message=sentinel.message)
        handler2.assert_called_once_with(message=sentinel.message)
        self.assertEquals(2, len(self.callback))

    def test_many_handlers(self):
        "General version of `test_2_handlers`"
        handlers = [Mock() for _ in xrange(1, 100)]
        for handler in handlers:
            self.callback += handler
        self.assertEquals(len(handlers), len(self.callback))
        for handler in handlers:
            self.assertFalse(handler.called)
        self.callback(message=sentinel.message)
        for handler in handlers:
            handler.assert_called_once_with(message=sentinel.message)
        self.assertEquals(len(handlers), len(self.callback))

    def test_many_unhandle(self):
        "Unhandle many"
        real_handlers = [Mock() for _ in xrange(1, 100)]
        to_unhandle = [Mock() for _ in xrange(1, 20)]
        for handler in chain(real_handlers, to_unhandle):
            self.callback += handler
        self.assertEquals(
            len(real_handlers) + len(to_unhandle), len(self.callback))
        for handler in to_unhandle:
            self.callback -= handler
        self.assertEquals(len(real_handlers), len(self.callback))
        self.callback(message=sentinel.message)
        for handler in to_unhandle:
            self.assertFalse(handler.called)
        for handler in real_handlers:
            handler.assert_called_once_with(message=sentinel.message)

    def test_handle_exception(self):
        "Test that an exception is raised by the callback method"
        handler = Mock(side_effect=self._always_raise)
        self.callback += handler
        self.assertRaises(Exception, self.callback, message=sentinel.message)

    def test_2_handle_exception(self):
        "Test that an exception is raised by the callback method"
        handler1 = Mock(side_effect=self._always_raise)
        handler2 = Mock()
        self.callback += handler1
        self.callback += handler2
        self.assertRaises(Exception, self.callback, message=sentinel.message)
        # Because the collection of handlers in the `Signal` is a
        # `set` the 'firing' order is undefined. However, if handler2
        # is called, we assert that it is called correctly here.
        if handler2.called:
            handler2.assert_called_once_with(message=sentinel.message)

    @staticmethod
    def _always_raise(*args, **kwargs):
        "Always raise `Exception` with no arguments"
        raise Exception()


@raises(KeyError)
def test_removing_non_existing_handler_fails():
    e = Signal()
    e -= 'irrelevant'


def test_removing_handler_works():
    e = Signal()
    h = Mock()
    e += h
    e -= h
    e.fire()
    eq_(h.called, False)
