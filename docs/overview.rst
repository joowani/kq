Getting Started
---------------

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
    [INFO] Starting Worker(topic=foobar) ...


Enqueue the function call as a job:

.. code-block:: python

    # Import the blocking function
    from my_module import my_func

    # Initialize a queue
    from kq import Queue
    q = Queue()

    # Enqueue the function call
    q.enqueue(my_func, 1, 2, baz=3)


Sit back and watch the worker process the job in the background:

.. code-block:: bash

    ~$ kq worker --verbose
    [INFO] Starting Worker(topic=default) ...
    [INFO] Processing Record(topic=default, partition=5, offset=3) ...
    [INFO] Running Job 1b92xle0: my_module.my_func(1, 2, baz=3) ...
    [INFO] Job 1b92xle0 returned: (1, 2, 3)


And that's essentially all there is to KQ! Continue for more information.