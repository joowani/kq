KQ: Kafka-based Job Queue for Python
------------------------------------

Welcome to the documentation for **KQ (Kafka Queue)**, Python library that lets you
enqueue and execute jobs asynchronously using `Apache Kafka`_.

KQ is built on top of kafka-python_.

Requirements
============

- `Apache Kafka`_ 0.9+
- Python 3.6+

Installation
============

Install using pip:

.. code-block:: bash

    pip install kq

Contents
========

.. toctree::
    :maxdepth: 1

    overview
    queue
    worker
    job
    message
    callback
    serializer
    logging

.. _Apache Kafka: https://kafka.apache.org
.. _kafka-python: https://github.com/dpkp/kafka-python
.. _GitHub: https://github.com/joowani/kq
