from smk.client import Smarkets
from smk.exceptions import (
    SmkError,
    ConnectionError,
    DecodeError,
    ParseError,
    )
from smk.session import Session


__version__ = '0.1.0'
__all__ = ['SmkError', 'ConnectionError', 'DecodeError',
           'ParseError', 'Smarkets', 'Session']


VERSION = tuple(map(int, __version__.split('.')))
