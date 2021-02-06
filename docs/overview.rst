Getting Started
---------------

Start your Kafka instance. Example using Docker_:

.. code-block:: bash

    docker run -p 9092:9092 -e ADV_HOST=127.0.0.1 lensesio/fast-data-dev

.. _Docker: https://github.com/lensesio/fast-data-dev

Define your KQ ```worker.py`` module:

.. code-block:: python

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

    python my_worker.py
    [INFO] Starting Worker(hosts=127.0.0.1:9092 topic=topic, group=group) ...

Enqueue a function call:

.. testcode::

    import requests

    from kafka import KafkaProducer
    from kq import Queue

    # Set up a Kafka producer.
    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

    # Set up a queue.
    queue = Queue(topic='topic', producer=producer)

    # Enqueue a function call.
    job = queue.enqueue(requests.get, 'https://google.com')

    # You can also specify the job timeout, Kafka message key and partition.
    job = queue.using(timeout=5, key=b'foo', partition=0).enqueue(requests.get, 'https://google.com')

Let the worker process it in the background:

.. code-block:: bash

    python my_worker.py
    [INFO] Starting Worker(hosts=127.0.0.1:9092, topic=topic, group=group) ...
    [INFO] Processing Message(topic=topic, partition=0, offset=0) ...
    [INFO] Executing job c7bf2359: requests.api.get('https://www.google.com')
    [INFO] Job c7bf2359 returned: <Response [200]>
