"Core Smarkets API exceptions"


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
