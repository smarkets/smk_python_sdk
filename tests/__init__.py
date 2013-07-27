import logging
import os
import unittest

from session_tests import (
    LoginTestCase,
    PingTestCase,
    OrderTestCase,
    QuoteTestCase,
    EventTestCase,
)
from threading_tests import ThreadingTestCase

from unit_tests import (
    CallbackTestCase,
    SmarketsTestCase,
    UuidTestCase,
)


def unit_tests(suite):
    "Add tests to a `unittest.TestSuite` containing only unit tests"
    suite.addTest(unittest.makeSuite(CallbackTestCase))
    suite.addTest(unittest.makeSuite(SmarketsTestCase))
    suite.addTest(unittest.makeSuite(UuidTestCase))


def integration_tests(
    suite,
    password_filename=None,
    market_filename=None,
    server=None,
    port=None,
        ssl=None):
    "Add tests to a `unittest.TestSuite` containing integration tests"
    # Use defaults from our test data
    if password_filename is None:
        password_filename = os.path.join(
            os.path.dirname(__file__), '..', '..', '..',
            'test-data', 'test_usernames.txt')
    if market_filename is None:
        market_filename = os.path.join(
            os.path.dirname(__file__), '..', '..', '..',
            'test-data', 'test_markets.txt')
    passwords = list(read_pair_file(password_filename))
    markets = list(read_pair_file(market_filename))
    for case_class in (
        LoginTestCase,
        PingTestCase,
        OrderTestCase,
        QuoteTestCase,
        EventTestCase,
        ThreadingTestCase,
    ):
        case_class.passwords = passwords
        case_class.markets = markets
        case_class.host = server
        case_class.port = port
        case_class.ssl = ssl
        suite.addTest(unittest.makeSuite(case_class))
    return suite


def read_pair_file(filename):
    "Read a file (consisting of a:b\n) and yield tuple pairs (a, b)"
    if filename is not None:
        try:
            pfile = open(filename)
            for line in pfile.readlines():
                yield tuple(line.rstrip('\n').split(':', 1))
            pfile.close()
        except IOError:
            # I'm going to swallow this and assume we couldn't find
            # the file
            logging.warning('got an IOError trying to read %s', filename)
            pass
