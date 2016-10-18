Decorator
---------

KQ provides a decorator which adds to the wrapped function a new method called
**delay**. The **delay** method takes the same set of arguments as the wrapped
function itself. When the method is called, instead of executing the function,
it enqueues it as a job. Here is an example:

Decorate a function in a module that workers can import:


.. code-block:: python

    from kq import Queue

    # Initialize the queue
    queue = Queue(topic='foobar')

    # Decorate a function to mark it as a job
    @queue.job
    def calculate_sum(a, b, c):
        return a + b + c


Start a KQ worker:

.. code-block:: bash

    ~$ kq worker --verbose
    [INFO] Starting Worker(topic=foobar) ...


Import the decorated function and call the new **delay** method:

.. code-block:: python

    from my_module import calculate_sum
    from kq import Job

    # The function can still be executed normally
    result = calculate_sum(1, 2, 3)
    assert result == 6

    # Call the delay method to enqueue the function call as a job
    result = calculate_sum.delay(1, 2, 3)
    assert isinstance(result, Job)


The worker processes the job in the background:

.. code-block:: bash

    ~$ kq worker --verbose
    [INFO] Starting Worker(topic=foobar) ...
    [INFO] Processing Record(topic=foobar, partition=1, offset=2) ...
    [INFO] Running Job 1b92xle0: my_module.calculate_sum(1, 2, 3) ...
    [INFO] Job 1b92xle0 returned: 6


The decorator is simply an alternative to the ``enqueue`` method.