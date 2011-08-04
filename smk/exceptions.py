"Core Smarkets API exceptions"


class SmkError(Exception):
    pass


class ConnectionError(SmkError):
    pass


class DecodeError(SmkError):
    pass


class ParseError(SmkError):
    pass
