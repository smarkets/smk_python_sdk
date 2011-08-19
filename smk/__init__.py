"Smarkets API package"
from smk.client import Smarkets
from smk.exceptions import (
    SmkError,
    ConnectionError,
    DecodeError,
    ParseError,
    SocketDisconnected,
    InvalidCallbackError,
    )
from smk.session import Session


__version__ = '0.1-alpha'
__all__ = ['SmkError', 'ConnectionError', 'DecodeError',
           'ParseError', 'SocketDisconnected', 'InvalidCallbackError',
           'Smarkets', 'Session']


VERSION = tuple((int(x) for x in __version__.split('.')))
