"Core Smarkets API exceptions"
# Copyright (C) 2011 Smarkets Limited <support@smarkets.com>
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

import sys as _sys

import six as _six


def reraise(exception):
    prev_cls, prev, tb = _sys.exc_info()
    _six.reraise(type(exception), exception, tb)


class Error(Exception):

    "General Smarkets API error"
    pass


class ConnectionError(Error):

    "TCP connection-related error"
    pass


class DecodeError(Error):

    "Header decoding error"
    pass


class ParseError(Error):

    "Error parsing a message or frame"
    pass


class SocketDisconnected(Error):

    "Socket was disconnected while reading"
    pass


class InvalidCallbackError(Error):

    "Invalid callback was specified"
    pass


class InvalidUrlError(Error):

    "Raised when a URL is invalid"
    pass


class DownloadError(Error):

    "Raised when a URL could not be fetched"
    pass
