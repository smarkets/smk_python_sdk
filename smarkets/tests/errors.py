from __future__ import absolute_import

from nose.tools import eq_, raises

from smarkets.errors import swallow


def throw_or_return(to_raise=None, to_return=None):
    if to_raise:
        raise to_raise  # pylint: disable=E0702

    if to_return:
        return to_return


class TestSwallow(object):

    def setup(self):
        self.fun = swallow(exceptions=Exception, default='default_value')(throw_or_return)

    def test_return_value_is_correct_in_case_of_no_exception(self):
        eq_(self.fun(to_return=1234), 1234)

    def test_right_exception_is_swallowed(self):
        self.fun(to_raise=Exception())

    @raises(SystemExit)
    def test_exceptions_other_than_specified_dont_get_swallowed(self):
        self.fun(to_raise=SystemExit(1))

    def test_default_value_is_returned_in_case_of_exception(self):
        eq_(self.fun(to_raise=Exception()), 'default_value')

    def test_exceptions_accept_single_exception(self):
        fun = swallow(exceptions=SystemExit)(throw_or_return)
        fun(to_raise=SystemExit)

    def test_eceptions_accept_many_exceptions(self):
        fun = swallow(exceptions=[SystemExit, KeyboardInterrupt])(throw_or_return)
        fun(to_raise=SystemExit)

    def test_swallow_works_as_context_manager(self):
        with swallow(KeyError):
            raise KeyError(1)

        try:
            with swallow(KeyError):
                raise ValueError(1)
        except ValueError:
            pass
