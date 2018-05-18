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

.. image:: https://img.shields.io/badge/python-3.5%2C%203.6-blue.svg
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

**KQ (Kafka Queue)** is a lightweight Python library which lets you queue and
execute jobs asynchronously using `Apache Kafka`_. It uses kafka-python_ under
the hood.

Announcements
=============

* KQ version `2.0.0`_ is now out!
* Please see the releases_ page for latest updates.

Requirements
============

* `Apache Kafka`_ 0.9+
* Python 3.5+

Installation
============

To install a stable version from PyPI_ (recommended):

.. code-block:: bash

    ~$ pip install kq

To install the latest version directly from GitHub_:

.. code-block:: bash

    ~$ pip install -e git+git@github.com:joowani/kq.git@master#egg=kq

You may need to use ``sudo`` depending on your environment.

Getting Started
===============

First, ensure that your Kafka instance is up and running:

.. code-block:: bash

    ~$ ./kafka-server-start.sh -daemon server.properties

Define your KQ worker module:

.. code-block:: python

    # my_worker.py

    import logging

    from kafka import KafkaConsumer
    from kq import Worker

    # Set up logging.
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger('kq.worker')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    # Set up a Kafka consumer.
    consumer = KafkaConsumer(
        bootstrap_servers='127.0.0.1:9092',
        group_id='group',
        auto_offset_reset='latest'
    )

    # Set up a worker.
    worker = Worker(topic='topic', consumer=consumer)
    worker.start()

Start the worker:

.. code-block:: bash

    ~$ python my_worker.py
    [INFO] Starting Worker(hosts=127.0.0.1:9092 topic=topic, group=group) ...

Enqueue a function call:

.. code-block:: python

    import requests

    from kafka import KafkaProducer
    from kq import Queue

    # Set up a Kafka producer.
    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

    # Set up a queue.
    queue = Queue(topic='topic', producer=producer)

    # Enqueue a function call.
    job = queue.enqueue(requests.get, 'https://www.google.com')

Sit back and watch the worker process it in the background:

.. code-block:: bash

    ~$ python my_worker.py
    [INFO] Starting Worker(hosts=127.0.0.1:9092, topic=topic, group=group) ...
    [INFO] Processing Message(topic=topic, partition=0, offset=0) ...
    [INFO] Executing job c7bf2359: requests.api.get('https://www.google.com')
    [INFO] Job c7bf2359 returned: <Response [200]>

**NEW in 2.0.0**: You can now specify the job timeout, message key and partition:

.. code-block:: python

    job = queue.using(timeout=5, key=b'foo', partition=0).enqueue(requests.get, 'https://www.google.com')

Check out the full documentation_ for more information.

Contributing
============

Please have a look at this page_ before submitting a pull request. Thanks!


Credits
=======

This project was inspired by RQ_.

.. _Apache Kafka: https://kafka.apache.org
.. _kafka-python: https://github.com/dpkp/kafka-python
.. _2.0.0: https://github.com/joowani/kq/releases/tag/2.0.0
.. _releases: https://github.com/joowani/kq/releases
.. _PyPI: https://pypi.python.org/pypi/kq
.. _GitHub: https://github.com/joowani/kq
.. _documentation: http://kq.readthedocs.io
.. _page: http://kq.readthedocs.io/en/master/contributing.html
.. _RQ: https://github.com/rq/rq
