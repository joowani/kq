KQ: Kafka Job Queue for Python
------------------------------

.. image:: https://img.shields.io/github/license/joowani/kq?color=bright
    :alt: GitHub License
    :target: https://github.com/joowani/kq/blob/main/LICENSE

.. image:: https://img.shields.io/badge/python-3.6%2B-blue
    :alt: Python Versions

**KQ (Kafka Queue)** is a Python library which lets you enqueue and execute jobs
asynchronously using `Apache Kafka`_. It uses kafka-python_ under the hood.

Requirements
============

- `Apache Kafka`_ 0.9+
- Python 3.6+

Installation
============

Install via pip_:

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
.. _pip: https://pip.pypa.io
