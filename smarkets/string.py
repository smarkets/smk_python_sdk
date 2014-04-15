# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import decorator
import six

__all__ = ('n', 'native_str_result', 'camel_case_to_underscores')

n_docstring = '''
Returns string as native str object. Encodes/decodes using UTF-8 when necessary.
:type string: bytes, str or unicode
:rtype: str
'''

if six.PY3:
    def n(string):
        n_docstring
        return string if isinstance(string, str) else string.decode('utf-8')
else:
    def n(string):
        n_docstring
        return string if isinstance(string, str) else string.encode('utf-8')


@decorator.decorator
def native_str_result(function, *args, **kwargs):
    '''
    '''
    return n(function(*args, **kwargs))

_camel_case_re = re.compile('([A-Z]+)')


def camel_case_to_underscores(name):
    return _camel_case_re.sub(r'_\1', name).lower().strip('_')
