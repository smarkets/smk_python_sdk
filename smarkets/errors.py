# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys as _sys
import six as _six


def reraise(exception):
    prev_cls, prev, tb = _sys.exc_info()
    _six.reraise(type(exception), exception, tb)


class Error(Exception):

    "Base class for every Smarkets error"
