from nose.tools import eq_

from smarkets.itertools import group, mapkeys, mapvalues


def test_mapkeys():
    eq_(mapkeys(str, {1: 'this', 2: 'that'}),
        {'1': 'this', '2': 'that'})


def test_mapvalues():
    eq_(mapvalues(tuple, {1: 'this', 2: 'that'}),
        {1: ('t', 'h', 'i', 's',), 2: ('t', 'h', 'a', 't',)})


def test_group():
    for i, n, o in (
        ('', 2, ()),
        ('A', 2, (('A',),)),
        ('AB', 2, (('A', 'B'),)),
        ('ABCDE', 2, (('A', 'B'), ('C', 'D'), ('E',))),
    ):
        yield check_group, i, n, o


def check_group(i, n, o):
    eq_(tuple(group(i, n)), tuple(o))
