# smk

Python API client for Smarkets.

## Installation

    $ sudo python setup.py install


## Getting Started

    >>> import logging
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> import smk
    >>> username = 'username'
    >>> password = 'password'
    >>> host = 'api-dev.corp.smarkets.com'
    >>> port = 3701
    >>> session = smk.Session(username, password, host, port)
    >>> client = smk.Smarkets(session)
    >>> client.login()
    >>> client.ping()
    >>> client.read()
    >>> market_id = '000000000000000000000001dc91c024'
    >>> client.subscribe(market_id) # subscribe to a market
    >>> client.read()
    >>> quantity = 400000
    >>> price = '25'
    >>> side = smk.seto_pb2.buy
    >>> contract_id = '000000000000000000000002ab9acccc'
    >>> client.order(quantity, price, side, market_id, contract_id)
    >>> client.read()


### Resuming a session

When resuming a session you need to know the incoming and outgoing
sequence numbers you were using when the session was last used, from
the example above they will now both be 5.

    >>> username = 'username'
    >>> password = 'password'
    >>> host = 'api-dev.corp.smarkets.com'
    >>> port = 3701
    >>> session_id = 'session-id'
    >>> inseq = 5
    >>> outseq = 5
    >>> session = smk.Session(
    >>>     username, password, host, port, session_id, inseq, outseq)
    >>> client = smk.Smarkets(session)
    >>> client.login()


### Registering callbacks

    >>> def login_response(self, msg):
    >>>     print "Session", msg.sequenced.message_data.login_response.session
    >>> def order_accepted(self, msg):
    >>>     print "Order Accepted", \
    >>>         msg.sequenced.message_data.order_accepted.seq, \
    >>>         msg.sequenced.message_data.order_accepted.order
    >>> def order_executed(self, msg):
    >>>     print "Order Executed", \
    >>>         msg.sequenced.message_data.order_executed.order, \
    >>>         msg.sequenced.message_data.order_executed.price, \
    >>>         msg.sequenced.message_data.order_executed.quantity
    >>> def order_cancelled(self, msg):
    >>>     print "Order Cancelled", \
    >>>         msg.sequenced.message_data.order_cancelled.order, \
    >>>         msg.sequenced.message_data.order_cancelled.reason
    >>> def pong(self, msg):
    >>>     print "Pong"
    >>> def market_quotes(self, msg):
    >>>     print "Quotes ", msg.sequenced.message_data.market_quotes.group
    >>> client.add_handler('login_response', login_response)
    >>> client.add_handler('order_accepted', order_accepted)
    >>> client.add_handler('order_executed', order_executed)
    >>> client.add_handler('order_cancelled', order_cancelled)
    >>> client.add_handler('pong', pong)
    >>> client.add_handler('market_quotes', market_quotes)
