# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import unittest

import pytz
from nose.tools import eq_

from smarkets.datetime import iso8601_to_datetime


class DateTests(unittest.TestCase):

    def test_valid_iso_conversion(self):
        valid_iso_dates = (
            ('2009-04-24T15:48:26,000000Z', datetime.datetime(2009, 0o4, 24, 15, 48, 26, 0, pytz.utc)),
            ('2009-04-24T15:48:26', datetime.datetime(2009, 0o4, 24, 15, 48, 26, 0, pytz.utc)),
            ('2009-04-24T15:48:26.000000Z', datetime.datetime(2009, 0o4, 24, 15, 48, 26, 0, pytz.utc)),
        )
        for iso, real_date in valid_iso_dates:
            result = iso8601_to_datetime(iso)
            eq_(result, real_date, "Date %s didn't match %s" % (result, real_date))

    def test_invalid_iso_conversion(self):
        invalid_iso_dates = (
            'gibberish',
        )
        for iso in invalid_iso_dates:
            result = iso8601_to_datetime(iso)
            eq_(result, None, "Date %s didn't fail" % iso)
