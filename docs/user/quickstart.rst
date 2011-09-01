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

    >>> import smarkets
    >>> username = 'username'
    >>> password = 'password'
    >>> settings = smarkets.SessionSettings(username, password)
    >>> settings.host = 'api.smarkets.com'
    >>> settings.port = 3701

Then, we create the :class:`Session` object which we will use to keep
track of sequence numbers::

    >>> session = smarkets.Session(settings)

Finally, the :class:`Client` class is the higher-level wrapper which
allows us to send and handle messages::

    >>> client = smarkets.Smarkets(session)

Now, let's login! ::

    >>> client.login()

We can also test our connectivity::

    >>> client.ping()
    >>> client.flush()
    >>> client.read()  # this will read a 'pong' response

And logout::

    >>> client.logout()


Resuming a session
------------------

One of the key aspects of our streaming API is the ability to resume a
session in the event of a network failure or software bug which closes
a socket connection prematurely.

We can re-use our :class:`SessionSettings` object from the above
section. However, when creating the :class:`Session` object, we
specify three additional parameters: **session_id**, **inseq** and
**outseq** ::

    >> session = smarkets.Session(settings, session_id='foo', inseq=3, outseq=3)

The rest works normally::

    >>> client = smarkets.Smarkets(session)
    >>> client.login()

However, because our login message contains a session id which we
intend to resume (and the sequence numbers we last saw and sent), the
client will implicitly request a **replay** to collect the missing
messages.


Placing a bet
-------------

The :class:`Order` class provides the mechanism to send a message to
create a new order::

    >>> order = smarkets.Order()
    >>> order.quantity = 400000  # 40.0000 GBP payout
    >>> order.price = 2500  # 25.00%
    >>> order.side = smarkets.Order.BUY
    >>> order.market = client.str_to_uuid128('fc024')
    >>> order.contract = client.str_to_uuid128('fcccc')

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
    >>>         message_name, text_format.MessageToString(message))

First, we register the callback for the eto.login_response message::

    >>> client.add_handler('eto.login_response', login_response_callback)

We can also register a **global** handler which will be called for
every message received::

    >>> client.add_global_handler(global_callback)
