"Core Smarkets API exceptions"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

from smarkets.errors import Error as _Error


class ConnectionError(_Error):

    "TCP connection-related error"
    pass


class DecodeError(_Error):

    "Header decoding error"
    pass


class ParseError(_Error):

    "Error parsing a message or frame"
    pass


class SocketDisconnected(_Error):

    "Socket was disconnected while reading"
    pass


class InvalidCallbackError(_Error):

    "Invalid callback was specified"
    pass


class InvalidUrlError(_Error):

    "Raised when a URL is invalid"
    pass


class DownloadError(_Error):

    "Raised when a URL could not be fetched"
    pass
