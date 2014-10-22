from __future__ import absolute_import, division, print_function, unicode_literals

from eventlet import spawn
from nose.tools import eq_
from six.moves import xrange

from smarkets.greenlet import cooperative_iter


def test_cooperative_iter_is_cooperative():
    storage = []

    def process_stuff(identifier, count):
        for i in cooperative_iter(xrange(count), interval=0.05):
            storage.append(identifier)

    t1 = spawn(process_stuff, 'A', 2)
    t2 = spawn(process_stuff, 'B', 2)
    for t in t1, t2:
        t.wait()
    eq_(storage, ['A', 'B', 'A', 'B'])


def test_cooperative_iter_yields_correct_data():
    data = ['a', 'b', 'c']
    eq_(list(cooperative_iter(data)), data)
