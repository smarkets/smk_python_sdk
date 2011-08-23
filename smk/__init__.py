"Smarkets API package"
# Copyright (C) 2011 Smarkets Limited support@smarkets.com
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
import inspect

from smk.client import Smarkets
from smk.event import (
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
from smk.exceptions import (
    SmkError,
    ConnectionError,
    DecodeError,
    ParseError,
    SocketDisconnected,
    InvalidCallbackError,
    )
from smk.session import Session


__version__ = '0.1.0'

__all__ = sorted(name for name, obj in locals().items()
                 if not (name.startswith('_') or inspect.ismodule(obj)))

VERSION = tuple((int(x) for x in __version__.split('.')))
