Logging
-------

By default, :doc:`queues <queue>` log messages to ``kq.queue`` logger, and
:doc:`workers <worker>` to ``kq.worker`` logger. You can use these default loggers
or set your own during queue/worker initialization.

**Example:**

.. testcode::

    import logging

    from kafka import KafkaConsumer, KafkaProducer
    from kq import Queue, Worker

    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Set up "kq.queue" logger.
    queue_logger = logging.getLogger('kq.queue')
    queue_logger.setLevel(logging.INFO)
    queue_logger.addHandler(stream_handler)

    # Set up "kq.worker" logger.
    worker_logger = logging.getLogger('kq.worker')
    worker_logger.setLevel(logging.DEBUG)
    worker_logger.addHandler(stream_handler)

    # Alternatively, you can inject your own loggers.
    queue_logger = logging.getLogger('your_worker_logger')
    worker_logger = logging.getLogger('your_worker_logger')

    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
    consumer = KafkaConsumer(bootstrap_servers='127.0.0.1:9092', group_id='group')

    queue = Queue('topic', producer, logger=queue_logger)
    worker = Worker('topic', consumer, logger=worker_logger)
