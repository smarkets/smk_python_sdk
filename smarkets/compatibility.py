print('Stop using this module, use six for ConfigParser and '
      'use regular SysLogHandler with Python 2.7+/Python3.x')

from logging.handlers import SysLogHandler

__all__ = ['configparser', 'UTFFixedSysLogHandler']

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


UTFFixedSysLogHandler = SysLogHandler
