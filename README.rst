smk-python-sdk
==============

.. image:: https://travis-ci.org/smarkets/smk_python_sdk.png?branch=master
   :alt: Build status
   :target: https://travis-ci.org/smarkets/smk_python_sdk

Smarkets Streaming API Python client.

Compatible with Python 2.7, 3.5 and PyPy 1.9+.

Documentation: http://smarkets-python-sdk.readthedocs.org/en/latest/


Installing using source distribution
------------------------------------

When you install smk-python-sdk using PyPI distribution there are no non-Python dependencies. All the Python dependencies will be fetched for you when you install smk-python-sdk.

PyPI page: https://pypi.python.org/pypi/smk_python_sdk

::

    pip install smk-python-sdk


Getting Started
---------------

.. code-block:: python

    import logging
    logging.basicConfig(level=logging.DEBUG)

    from smarkets.streaming_api.api import (
        SessionSettings, Session, StreamingAPIClient,
    )

    username = 'username'
    password = 'password'

    settings = SessionSettings(username, password)
    settings.host = 'stream.smarkets.com'

    session = Session(settings)

    client = StreamingAPIClient(session)

    client.login()
    client.ping()
    client.read()
    client.flush()

    client.logout()


Registering callbacks
'''''''''''''''''''''

.. code-block:: python

    def login_response(message):
        print('eto.login_response', msg)

    def global_callback(name, message):
        print(name, message.protobuf)

    client.add_handler('eto.login_response', login_response)
    client.add_global_handler(global_callback)


Placing orders
'''''''''''''''''''''

.. code-block:: python

    from smarkets.streaming_api.api import SIDE_BID
    from smarkets.streaming_api.seto import OrderCreate

    def order_accepted(message):
        reference = message.order_accepted.reference
        order_id = message.order_accepted.order_id
        print(
            'ORDER_ACCEPTED: reference {} corresponding to order_id {}'.format(
                reference, order_id,
            )
        )

    def order_rejected(message):
        reference = message.order_rejected.reference
        reason = message.order_rejected.reason
        print('ORDER_REJECTED with reference {} with reason {}'.format(reference, reason))

    client.add_handler('seto.order_accepted', order_accepted)
    client.add_handler('seto.order_rejected', order_rejected)

    market_id = 100000
    contract_id = 200000

    order = OrderCreate()
    order.quantity = 400000 # £40 payout
    order.price = 2500 # 25.00%
    order.side = SIDE_BID
    order.market_id = market_id
    order.contract_id = contract_id

    client.send(order)
    client.flush()


Cancelling orders
'''''''''''''''''''''

.. code-block:: python

    from smarkets.streaming_api.seto import OrderCancel

    order_id = ...  # received in seto.order_accepted message

    def order_cancelled(message):
        order_id = message.order_cancelled.order_id
        reason = message.order_cancelled.reason
        print('ORDER_CANCELLED order_id {} with reason {}'.format(order_id, reason))

    def order_cancel_rejected(message):
        order_id = message.order_cancel_rejected.order_id
        reason = message.order_cancel_rejected.reason
        print('ORDER_CANCEL_REJECTED: with order_id {} with reason {}'.format(order_id, reason))

    client.add_handler('seto.order_cancelled', order_cancelled)
    client.add_handler('seto.order_cancel_rejected', order_cancel_rejected)

    cancel = OrderCancel()
    cancel.order_id = order_id
    client.send(cancel)
    client.flush()


Thread Safety
-------------

Functions and class members contained in this package are thread safe. Instance members are *not* thread safe.

Development
-----------

GitHub repository: https://github.com/smarkets/smk_python_sdk/

Non-Python dependencies:

* piqi
* Google protocol buffers compiler and libraries

You can install Python dependencies by executing:

::

    pip install -r requirements.txt

To build and install call:


::

    python setup.py clean build install

Note: building the package does not fetch the most recent piqi files from their respective locations in setup.py.
In order to do so, you must call python setup.py clean, and then python setup.py build.

License
-------

Copyright (C) Smarkets Limited <support@smarkets.com>

This module is released under the MIT License: http://www.opensource.org/licenses/mit-license.php (or see the LICENSE file)
