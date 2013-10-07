.. _introduction:

Introduction
============

Philosophy
----------

The main driving force behind the development of the Smarkets
streaming API is efficiency. Many other applications in our industry
rely on "polling" a service in order to provide a real-time view of
changing data. While the streaming API can be used in a "synchronous"
manner by making a request and waiting for a response, it is often far
more efficient to design an application asynchronously. Asynchronous
messaging allows for more flexible patterns and techniques like
pipelining.

The streaming API also uses framed `protocol buffers`_ to define the
wire format, so parsing messages is relatively fast and simple. We
will endeavour to maintain backwards compatibility as we release newer
revisions of the API. Protocol buffers definitions provide a `decent
facility for doing so
<http://code.google.com/apis/protocolbuffers/docs/proto.html#updating>`_.

.. _`protocol buffers`: http://code.google.com/p/protobuf/


MIT License
-----------

In selecting a software license, we aimed to choose one which allows
third-party application developers flexibility in using the code we
provide.

The Smarkets Python API Client is released under the `MIT License`_.

.. _`MIT License`: http://www.opensource.org/licenses/mit


Smarkets Python API Client License
----------------------------------

    Copyright (c) 2011 Smarkets Limited

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
