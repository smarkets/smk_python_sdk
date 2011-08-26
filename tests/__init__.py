import logging
import os
import unittest

from session_tests import (
    BasicTestCase,
    LoginTestCase,
    OrderTestCase,
    QuoteTestCase,
    EventTestCase,
)
from threading_tests import ThreadingTestCase


def all_tests(
    password_filename=None,
    market_filename=None,
    server='127.0.0.1',
    port=3701,
    skip_online=False):
    "Return a unittest.TestSuite containing runnable tests"
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    if not skip_online:
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
    if not skip_online:
        for case_class in (
            LoginTestCase,
            OrderTestCase,
            QuoteTestCase,
            EventTestCase,
            ThreadingTestCase,
            ):
            case_class.passwords = passwords
            case_class.markets = markets
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
