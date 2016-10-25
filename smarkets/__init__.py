# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

__version__ = '6.1.0'


def private(something):
    something.__private__ = True
    return something

__all__ = ()
