"Core Smarkets API exceptions"


class SmkError(Exception):
    "General Smarkets API error"
    pass


class ConnectionError(SmkError):
    "TCP connection-related error"
    pass


class DecodeError(SmkError):
    "Header decoding error"
    pass


class ParseError(SmkError):
    "Error parsing a message or frame"
    pass
