.. _api:

API
===

.. module:: smarkets

This part of the documentation is a reference for the various classes
necessary to develop with the client library.


Session
-------

.. autoclass:: Session
   :inherited-members:


SessionSettings
~~~~~~~~~~~~~~~

.. autoclass:: SessionSettings
   :inherited-members:


Client
------

.. autoclass:: Smarkets
   :inherited-members:

Orders
~~~~~~

.. autoclass:: Order
   :inherited-members:

Events
~~~~~~

.. autoclass:: EventsRequest
   :inherited-members:

.. autoclass:: Politics
   :inherited-members:
.. autoclass:: CurrentAffairs
   :inherited-members:
.. autoclass:: TvAndEntertainment
   :inherited-members:
.. autoclass:: SportByDate
   :inherited-members:
.. autoclass:: FootballByDate
   :inherited-members:
.. autoclass:: HorseRacingByDate
   :inherited-members:
.. autoclass:: TennisByDate
   :inherited-members:
.. autoclass:: SportOther
   :inherited-members:


Internals
---------

These are largely internal classes, but the documentation is included
for debugging or extending the functionality provided.

Exceptions
~~~~~~~~~~

.. module:: smarkets.exceptions

.. autoexception:: Error

.. autoexception:: ConnectionError
.. autoexception:: DecodeError
.. autoexception:: ParseError
.. autoexception:: SocketDisconnected
.. autoexception:: InvalidCallbackError


Classes
~~~~~~~

.. module:: smarkets.sessions

.. autoclass:: SessionSocket
   :inherited-members:
