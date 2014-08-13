# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_

from smarkets.uuid import int_to_uuid, uid_or_int_to_int


def test_uid_or_int_to_int():
    eq_(uid_or_int_to_int(1234, 'irrelevant'), 1234)
    eq_(uid_or_int_to_int(int_to_uuid(5454, 'Contract'), 'Contract'), 5454)

    try:
        uid_or_int_to_int(int_to_uuid(1234, 'Market'), 'Event')
        assert False, 'Should have failed'
    except ValueError:
        pass
