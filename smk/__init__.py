"Smarkets API package"
from smk.client import Smarkets
from smk.exceptions import (
    SmkError,
    ConnectionError,
    DecodeError,
    ParseError,
    InvalidCallbackError,
    )
from smk.session import Session


__version__ = '0.1.0'
__all__ = ['SmkError', 'ConnectionError', 'DecodeError',
           'ParseError', 'InvalidCallbackError',
           'Smarkets', 'Session']


VERSION = tuple((int(x) for x in __version__.split('.')))
