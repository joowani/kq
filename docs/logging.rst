Logging
-------

By default KQ logs messages using the ``kq`` logger.

Here is an example showing how the logger can be enabled and customized:

.. code-block:: python

    import logging

    from kq import Queue

    logger = logging.getLogger('kq')

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Attach a handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Enqueue function calls
    q = Queue()
    q.enqueue(int, 1)
    q.enqueue(str, 1)
    q.enqueue(bool, 1)


The logging output for above would look something like this:

.. code-block:: bash

    [INFO] Enqueued: Job(id='64ee47d', topic='default', func=<class 'int'> ...)
    [INFO] Enqueued: Job(id='4578f57', topic='default', func=<class 'str'> ...)
    [INFO] Enqueued: Job(id='792643c', topic='default', func=<class 'bool'> ...)
