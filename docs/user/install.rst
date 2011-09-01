.. _install:

Installation
============

This covers the basic installation of the Smarkets API Client which is
obviously necessary to get started.

Requirements
------------

These packages are necessary at runtime.

* `Protocol buffers`_ 2.3.0 or 2.4.1

These are required to build from source and run unit tests, etc.

* `cURL`_
* `mock`_
* `piqi`_

.. _`Protocol buffers`: http://code.google.com/p/protobuf/downloads/list
.. _`cURL`: http://curl.haxx.se/
.. _`mock`: http://pypi.python.org/pypi/mock
.. _`piqi`: http://piqi.org/downloads/

Pip
---

Install the client with `pip`_::

    $ pip install smk_python_sdk

.. _`pip`: http://www.pip-installer.org

Github
------

Smarkets makes its open source development activities available on
`GitHub`_, and the Python API Client is `available there
<https://github.com/smarkets/smk_python_sdk>`_.

Clone the public master branch::

    $ git clone https://github.com/smarkets/smk_python_sdk.git

Or, download a `.tar.gz`_::

    $ curl -O https://github.com/smarkets/smk_python_sdk/tarball/master

Or, a `.zip`_::

    $ curl -O https://github.com/smarkets/smk_python_sdk/zipball/master

.. _`.tar.gz`: https://github.com/smarkets/smk_python_sdk/tarball/master
.. _`.zip`: https://github.com/smarkets/smk_python_sdk/zipball/master

Installing from source
----------------------

Once you have downloaded a copy of the source, you can install it into
site-packages::

    $ python setup.py build install

The build target will download the necessary files to generate the
protobuf modules. Make sure you have satisfied the `requirements`_
listed above.
