import unittest

from session_tests import SessionTestCase
from threading_tests import ThreadingTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SessionTestCase))
    suite.addTest(unittest.makeSuite(ThreadingTestCase))
    return suite
