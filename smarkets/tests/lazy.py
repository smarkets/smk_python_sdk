from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_
from six.moves import xrange

from smarkets.lazy import LazyCall


def test_general_lazycall_behaviour():
    counter = [0]

    def computation(*args, **kwargs):
        eq_((args, kwargs), ((1, 2), {'a': 'b'}))
        counter[0] += 1
        return 'result value'

    eq_(counter[0], 0)
    result = LazyCall(computation, 1, 2, a='b')
    eq_(counter[0], 0)

    for i in xrange(3):
        eq_(result.get_value(), 'result value')
        eq_(counter[0], 1)

    eq_('%s' % result, 'result value')
