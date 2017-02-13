.. _quickstart:

Quickstart
==========

.. module:: smarkets.clients

This quickstart guide assumes you have already installed the
client. If you haven't, read :ref:`Installation <install>` first.


Setting up logging
------------------

When developing, it's often useful to turn on debug logging console output::

    import logging
    logging.basicConfig(level=logging.DEBUG)


Starting a session
------------------

In order to do anything meaningful with the API, you must first start
a new session. We import the base module and create our
:class:`SessionSettings` object::

    >>> from smarkets.streaming_api.api import (
    ...     BUY, SELL, OrderCreate, Session, SessionSettings, StreamingAPIClient)
    >>> username = 'username'
    >>> password = 'password'
    >>> settings = SessionSettings(username, password)
    >>> settings.host = 'api.smarkets.com'
    >>> settings.port = 3701

Then, we create the :class:`Session` object which we will use to keep
track of sequence numbers::

    >>> session = Session(settings)

Finally, the :class:`Client` class is the higher-level wrapper which
allows us to send and handle messages::

    >>> client = StreamingAPIClient(session)

Now, let's login! ::

    >>> client.login()

We can also test our connectivity::

    >>> client.ping()
    >>> client.flush()
    >>> client.read()  # this will read a 'pong' response

And logout::

    >>> client.logout()


Placing a bet
-------------

The :class:`Order` class provides the mechanism to send a message to
create a new order::

    >>> order = OrderCreate()
    >>> order.quantity = 400000  # 40.0000 GBP payout
    >>> order.price = 2500  # 25.00%
    >>> order.side = BUY
    >>> order.market_id = some_market
    >>> order.contract_id = some_contract

The above order is a **buy** (or **back**) at 25.00% (or 4.0 in
decimal format) for a £40.00 return. The buyer's liability if the
execution is at 25.00% will be £10.00.

Now, we send the create message::

    >>> client.order(order)
    >>> client.flush()


Registering callback functions
------------------------------

We can register some relatively simple callback functions for various
messages. This example uses the text_format module from the protocol
buffers package to simply print the message to stdout::

    >>> from google.protobuf import text_format
    >>> def login_response_callback(message):
    >>>     print "Received a eto.login_response: %s" % (
    >>>         text_format.MessageToString(message))
    >>> def global_callback(message_name, message):
    >>>     print "[global] Received a %s: %s" % (
    >>>         message_name, text_format.MessageToString(message.protobuf))

First, we register the callback for the eto.login_response message::

    >>> client.add_handler('eto.login_response', login_response_callback)

We can also register a **global** handler which will be called for
every message received::

    >>> client.add_global_handler(global_callback)
