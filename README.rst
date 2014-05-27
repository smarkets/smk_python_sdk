smk-python-sdk
==============

.. image:: https://travis-ci.org/smarkets/smk_python_sdk.png?branch=master
   :alt: Build status
   :target: https://travis-ci.org/smarkets/smk_python_sdk

Smarkets Python library (streaming API client, id generation, more to come).

Compatible with Python 2.7 and PyPy 1.9+.

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
        BUY, GOOD_TIL_CANCELLED, OrderCreate, SessionSettings, Session, StreamingAPIClient)

    username = 'username'
    password = 'password'

    settings = SessionSettings(username, password)
    settings.host = 'api.smarkets.com'
    settings.port = 3701

    session = Session(settings)

    client = StreamingAPIClient(session)

    client.login()
    client.ping()
    client.read()
    client.flush()

    market_id = client.str_to_uuid128('fc024')

    order = OrderCreate()
    order.quantity = 400000 # £40 payout
    order.price = 2500 # 25.00%
    order.side = BUY
    order.market = market_id
    order.contract = client.str_to_uuid128('fcccc')
    order.time_in_force = GOOD_TIL_CANCELLED

    client.send(order)
    client.logout()


Registering callbacks
'''''''''''''''''''''

.. code-block:: python

    from google.protobuf import text_format

    def login_response(msg):
        print("eto.login_response", text_format.MessageToString(msg))

    def global_callback(name, msg):
        print(name, text_format.MessageToString(msg))

    client.add_handler('eto.login_response', login_response)
    client.add_global_handler(global_callback)


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

    pip install -r requirements-dev-py2.txt

To build and install call:


::

    python setup.py clean build install

Note: building the package does not fetch the most recent piqi files from their respective locations in setup.py.
In order to do so, you must call python setup.py clean, and then python setup.py build.

License
-------

Copyright (C) 2011-2013 Smarkets Limited <support@smarkets.com>

This module is released under the MIT License: http://www.opensource.org/licenses/mit-license.php (or see the LICENSE file)
