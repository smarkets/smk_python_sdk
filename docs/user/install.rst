.. _install:

Installation
============

This covers the basic installation of the Smarkets API Client which is
obviously necessary to get started.

Requirements
------------

These packages are necessary at runtime.

* `protobuf` Python package, version 2.5.0 or higher (`smk-python-sdk` package installation process will automatically install it)

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

    $ pip install smk-python-sdk

.. _`pip`: http://www.pip-installer.org


Updating the SDK
----------------

Minor updates (0.5.0 to 0.5.1) are backwards compatible. Major updates (for example 0.5.1 to 0.6.0) are not necessarily backwards compatible, please consult SDK :ref:`changelog`.

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
