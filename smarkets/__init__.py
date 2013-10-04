"Smarkets API package"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import inspect
import os

if 'READTHEDOCS' in os.environ:
    from mock import Mock
    import sys

    sys.modules['smarkets.streaming_api.eto'] = sys.modules['smarkets.streaming_api.seto'] = Mock()

__version__ = '0.6.0c1'

__all__ = sorted(name for name, obj in locals().items()
                 if not (name.startswith('_') or inspect.ismodule(obj)))
