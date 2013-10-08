# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import eq_
from six import PY3

from smarkets.string import n, native_str_result


class TestString(object):
    binary_version = 'ąę'.encode('utf-8')
    unicode_version = 'ąę'
    inputs = (binary_version, unicode_version)
    output = unicode_version if PY3 else binary_version

    def test_n(self):
        for input in self.inputs:
            yield self.check_n, input, self.output

    def check_n(self, input, output):
        eq_(n(input), output)

    def test_native_str_result(self):
        for input in self.inputs:
            yield self.check_native_str_result, input, self.output

    def check_native_str_result(self, input, output):
        @native_str_result
        def f():
            return input

        eq_(f(), output)
