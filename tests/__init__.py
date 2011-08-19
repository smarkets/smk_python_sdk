import unittest

from session_tests import SessionTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SessionTestCase))
    return suite
