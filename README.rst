KQ: Kafka-based Job Queue for Python
------------------------------------

.. image:: https://travis-ci.org/joowani/kq.svg?branch=master
    :target: https://travis-ci.org/joowani/kq
    :alt: Build Status

.. image:: https://readthedocs.org/projects/kq/badge/?version=latest
    :target: http://kq.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/kq.svg
    :target: https://badge.fury.io/py/kq
    :alt: Package Version

.. image:: https://img.shields.io/badge/python-2.7%2C%203.4%2C%203.5-blue.svg
    :target: https://github.com/joowani/kq
    :alt: Python Versions

.. image:: https://coveralls.io/repos/github/joowani/kq/badge.svg?branch=master
    :target: https://coveralls.io/github/joowani/kq?branch=master
    :alt: Test Coverage

.. image:: https://img.shields.io/github/issues/joowani/kq.svg
    :target: https://github.com/joowani/kq/issues
    :alt: Issues Open

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/joowani/kq/master/LICENSE
    :alt: MIT License

|

KQ (Kafka Queue) is a lightweight Python library which provides a simple API
to process jobs asynchronously in the background. It uses `Apache Kafka`_ and
is designed primarily for ease of use.

.. _Apache Kafka: https://kafka.apache.org


Requirements
============

- Apache Kafka 0.9+
- Python 2.7+ 3.4+ or 3.5+


Getting Started
===============

First, ensure that your Kafka instance is up and running:

.. code-block:: bash

    # This command is just an example
    ~$ ./kafka-server-start.sh -daemon server.properties


Let's say you want to run the following function asynchronously:

.. code-block:: python

    import time

    def my_func(foo, bar, baz=None):
        """This is a blocking function."""
        time.sleep(10)
        return foo, bar, baz


Start a KQ worker:

.. code-block:: bash

    ~$ kq worker --verbose
    [INFO] Starting Worker(topic=default) ...


Enqueue the function call as a job:

.. code-block:: python

    # Import the blocking function
    from my_module import my_func

    # Initialize a queue
    from kq import Queue
    q = Queue()

    # Enqueue the function call
    q.enqueue(my_func, 1, 2, baz=3)


Sit back and watch the worker process it in the background:

.. code-block:: bash

    ~$ kq worker --verbose
    [INFO] Starting Worker(topic=default) ...
    [INFO] Processing Record(topic=default, partition=5, offset=3) ...
    [INFO] Running Job 1b92xle0: my_module.my_func(1, 2, baz=3) ...
    [INFO] Job 1b92xle0 returned: (1, 2, 3)


Check out the full documentation_ for more details!

.. _documentation: http://kq.readthedocs.io/en/master/


Installation
============

To install a stable version from PyPI_ (recommended):

.. code-block:: bash

    ~$ pip install kq


To install the latest version directly from GitHub_:

.. code-block:: bash

    ~$ pip install -e git+git@github.com:joowani/kq.git@master#egg=kq

You may need to use ``sudo`` depending on your environment setup.

.. _PyPI: https://pypi.python.org/pypi/kq
.. _GitHub: https://github.com/joowani/kq


Credits
=======

This project was inspired by RQ_ and built on top of kafka-python_.

.. _RQ: https://github.com/nvie/rq
.. _kafka-python: https://github.com/dpkp/kafka-python
