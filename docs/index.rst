KQ: Kafka-based Job Queue for Python
------------------------------------

Welcome to the documentation for **KQ (Kafka Queue)**, a light-weight Python
library which provides a simple API to queue and process jobs asynchronously
in the background. It is backed by `Apache Kafka`_ and designed primarily for
ease of use.

.. _Apache Kafka: https://kafka.apache.org


Requirements
============

- Apache Kafka 0.9+
- Python 2.7, 3.4, 3.5 or 3.6


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


Contents
========

.. toctree::
    :maxdepth: 1

    overview
    queue
    worker
    job
    manager
    decorator
    callback
    cli
    logging
    contributing


Credits
=======

This project was inspired by RQ_ and built on top of kafka-python_.

.. _RQ: https://github.com/nvie/rq
.. _kafka-python: https://github.com/dpkp/kafka-python