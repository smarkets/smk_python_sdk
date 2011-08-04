# smk

Python API client for Smarkets.

## Installation

    $ sudo python setup.py install


## Getting Started

    >>> from smk import Client
    >>> from smk.seto_pb2 import buy,sell
    >>> c = Client()
    >>> c.login('api-dev.corp.smarkets.com', 3701, 'you@domain.com', 'password')
    Session 37087943-b12f-4753-9af8-32814061097d
    >>> c.subscribe('000000000000000000000001dc91c024') # subscribe to a market
    >>> c.order(400000, '25', buy, '000000000000000000000001dc91c024', '000000000000000000000002ab9acccc')

### Resuming a session

When resuming a session you need to know the incoming and outgoing sequence numbers you were using when the session was last used, from the example above they will now both be 3.

    c.login('api-dev.corp.smarkets.com', 3701, 'you@domain.com', 'password', '37087943-b12f-4753-9af8-32814061097d', 3, 3)
