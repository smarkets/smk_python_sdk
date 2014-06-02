from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_

from smarkets.functools import memoized


def test_memoized():
    @memoized
    def my_sum(x, y):
        counter[0] += 1
        return x + y

    counter = [0]
    eq_(my_sum(1, 2), 3)
    eq_(counter[0], 1)
    eq_(my_sum(1, 2), 3)
    eq_(counter[0], 1)

    counter = [0]
    eq_(my_sum(1, y=2), 3)
    eq_(counter[0], 1)
    eq_(my_sum(1, y=2), 3)
    eq_(counter[0], 1)
