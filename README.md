# smarkets

Python API client for Smarkets.

## Getting the code

* https://github.com/smarkets/smk_python_sdk/

## Requirements

* Python >= 2.5
* Google protocol buffers compiler and libraries


## Installation

To install:

    $ pip install smk

or if that doesn't work:

    $ easy_install smk

or if you want to build it yourself:

    $ sudo python setup.py build install

## Getting Started

    >>> import logging
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> import smarkets
    >>> import smarkets.eto.piqi_pb2 as eto
    >>> import smarkets.seto.piqi_pb2 as seto
    >>> username = 'username'
    >>> password = 'password'
    >>> host = 'api.smarkets.com'
    >>> port = 3701
    >>> session = smarkets.Session(username, password, host, port)
    >>> client = smarkets.Smarkets(session)
    >>> client.login()
    >>> client.ping()
    >>> client.flush()
    >>> client.read()
    >>> market_id = seto.Uuid128()
    >>> market_id.low = 1234
    >>> client.subscribe(market_id) # subscribe to a market
    >>> client.flush()
    >>> client.read()
    >>> quantity = 400000 # £40 payout
    >>> price = 2500 # 25.00%
    >>> side = seto.SIDE_BUY
    >>> contract_id = seto.Uuid128()
    >>> contract_id.low = 5678
    >>> client.order(quantity, price, side, market_id, contract_id)
    >>> client.flush()
    >>> client.read()


### Resuming a session

When resuming a session you need to know the incoming and outgoing
sequence numbers you were using when the session was last used, from
the example above they will now both be 5.

    >>> username = 'username'
    >>> password = 'password'
    >>> host = 'api.smarkets.com'
    >>> port = 3701
    >>> session_id = 'session-id'
    >>> inseq = 5
    >>> outseq = 5
    >>> session = smarkets.Session(
    >>>     username, password, host, port, session_id, inseq, outseq)
    >>> client = smarkets.Smarkets(session)
    >>> client.login()
    >>> client.read()


### Registering callbacks

    >>> from google.protobuf import text_format
    >>> def login_response(msg):
    >>>     print "seto.login_response", text_format.MessageToString(msg)
    >>> def global_callback(name, msg):
    >>>     print name, text_format.MessageToString(msg)
    >>> client.add_handler('eto.login_response', login_response)
    >>> client.add_global_handler(global_callback)


## Connections

The `smarkets.sessions.SessionSocket` class wraps the vanilla Python
`socket.socket` class, providing the basic framing and padding
functionality. It opens a single TCP connection and keeps it open for
the duration of the session.


## Thread Safety

It is not safe to share `smarkets.clients.Smarkets` or
`smarkets.sessions.Session` objects between threads. Only a single
thread should call the `Smarkets.flush()` method (or others which
trigger a send) at a time. Similarly, a single thread should call
`Smarkets.read()` at a time. See the `ThreadingTestCase` in
`tests/threading_tests.py` for an example on appropriate
multi-threaded usage.
