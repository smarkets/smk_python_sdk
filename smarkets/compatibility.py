print('Stop using this module, use six for ConfigParser and '
      'use regular SysLogHandler with Python 2.7+/Python3.x')

from logging.handlers import SysLogHandler

__all__ = ['configparser', 'UTFFixedSysLogHandler', 'json']

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

try:
    import simplejson as json
except ImportError:
    import json


UTFFixedSysLogHandler = SysLogHandler
