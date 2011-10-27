"Smarkets API package"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import inspect

from smarkets.clients import Smarkets
from smarkets.events import (
    EventsRequest,
    Politics,
    CurrentAffairs,
    TvAndEntertainment,
    SportByDate,
    FootballByDate,
    HorseRacingByDate,
    TennisByDate,
    SportOther,
    )
from smarkets.exceptions import (
    Error,
    ConnectionError,
    DecodeError,
    ParseError,
    SocketDisconnected,
    InvalidCallbackError,
    )
from smarkets.orders import Order
from smarkets.sessions import Session, SessionSettings


__version__ = '0.3.1'

__all__ = sorted(name for name, obj in locals().items()
                 if not (name.startswith('_') or inspect.ismodule(obj)))

VERSION = tuple((int(x) for x in __version__.split('.')))
