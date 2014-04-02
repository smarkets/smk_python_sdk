from __future__ import absolute_import, division, print_function, unicode_literals

from smarkets.utils import timed


def test_timed_works_ok():
    times = [1.0, 4.14]

    def time():
        return times.pop(0)

    with timed(time=time) as result:
        try:
            result.get_value()
        except Exception:
            # We expect this, value won't be available inside timing context
            pass
        else:
            assert False, 'Did not raise'

    value = result.get_value()
    assert abs(value - 3140) < 0.001, value
