# smarkets

Python API client for Smarkets.

[![Build Status](https://travis-ci.org/smarkets/smk_python_sdk.png?branch=master)](https://travis-ci.org/smarkets/smk_python_sdk)

## Getting the code

* https://github.com/smarkets/smk_python_sdk/

## Requirements

* Python >= 2.6
* Google protocol buffers compiler and libraries

### For building the code, running tests and generating documentation

* curl
* mock
* nose
* pandoc
* Piqi
* sphinx
* pep8
* pylint

## Installation

To install:

    $ pip install smk_python_sdk

or if that doesn't work:

    $ easy_install smk_python_sdk

or if you want to build it yourself:

    $ sudo python setup.py build install

## Getting Started

```python
import logging
logging.basicConfig(level=logging.DEBUG)
import smarkets
username = 'username'
password = 'password'
settings = smarkets.SessionSettings(username, password)
settings.host = 'api.smarkets.com'
settings.port = 3701
session = smarkets.Session(settings)
client = smarkets.Smarkets(session)
client.login()
client.ping()
client.flush()
client.read()
market_id = client.str_to_uuid128('fc024')
client.subscribe(market_id) # subscribe to a market
client.flush()
client.read()
order = smarkets.Order()
order.quantity = 400000 # £40 payout
order.price = 2500 # 25.00%
order.side = smarkets.Order.BUY
order.market = market_id
order.contract = client.str_to_uuid128('fcccc')
client.order(order)
client.flush()
client.read()
client.logout()
```

### Resuming a session

When resuming a session you need to know the incoming and outgoing
sequence numbers you were using when the session was last used, from
the example above they will now both be 5.

```python
username = 'username'
password = 'password'
settings = smarkets.SessionSettings(username, password)
settings.host = 'api.smarkets.com'
settings.port = 3701
session_id = 'session-id'
inseq = 5
outseq = 5
session = smarkets.Session(settings, session_id, inseq, outseq)
client = smarkets.Smarkets(session)
client.login()
client.read()
```

### Registering callbacks

```python
from google.protobuf import text_format
def login_response(msg):
    print "eto.login_response", text_format.MessageToString(msg)
def global_callback(name, msg):
    print name, text_format.MessageToString(msg)
client.add_handler('eto.login_response', login_response)
client.add_global_handler(global_callback)
```

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
