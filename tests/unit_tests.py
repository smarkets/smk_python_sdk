import unittest

from mock import Mock

from smarkets.clients import Callback


class Handler(object):
    "Dummy which provides handle methods"
    def handle_message(self, _msg):
        "Simple message handler"
        pass

    def handle_global_message(self, _name, _msg):
        "Global message handler"
        pass


class CallbackTestCase(unittest.TestCase):
    "Test the `smarkets.Callback` class"
    def setUp(self):
        "Set up the tests"
        self.callback = Callback()

    def tearDown(self):
        "Tear down the test requirements"
        self.callback = None

    def test_simple_fire(self):
        "Test the simple case where the handler fires"
        handler = Handler()
        handler.handle_message = Mock()
        self.callback += handler.handle_message
        self.callback('foo')
        self.assertTrue(handler.handle_message.called)
        self.assertEquals(1, handler.handle_message.call_count)
