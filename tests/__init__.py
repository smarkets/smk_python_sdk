import unittest

from session_tests import (
    BasicTestCase,
    OrderTestCase,
    QuoteTestCase,
    EventTestCase,
)
from threading_tests import ThreadingTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    suite.addTest(unittest.makeSuite(OrderTestCase))
    suite.addTest(unittest.makeSuite(QuoteTestCase))
    suite.addTest(unittest.makeSuite(EventTestCase))
    suite.addTest(unittest.makeSuite(ThreadingTestCase))
    return suite
