Callbacks
---------

A callback can be passed to a KQ worker to extend the latter's functionality.
Whenever a KQ worker processes a job, the callback function (if given) is
automatically invoked. The callback must take exactly the following positional
arguments:

- status (str | unicode):
    The status of the job execution, which can be ``"timeout"``, ``"failure"``
    or ``"success"``.

- job (kq.job.Job):
    The namedtuple object representing the job executed.

- result (object):
    The result of the job execution.

- exception (Exception | None)
    The exception raised on job execution, or ``None`` if there were no errors.

- traceback (str | unicode | None)
    The traceback of the exception raised, or ``None`` if there were no errors.


Here is a trivial example:

.. code-block:: python

    import logging

    from kq import Job

    logger = logging.getLogger(__name__)

    def callback(status, job, result, exception, traceback):

        assert isinstance(job, Job)
        logger.info('Job UUID: {}'.format(job.id))
        logger.info('Enqueued at {}'.format(job.timestamp))
        logger.info('In topic: {}'.format(job.topic))
        logger.info('Function: {}'.format(job.func))
        logger.info('Arguments {}'.format(job.args))
        logger.info('Keyword arguments {}'.format(job.kwargs))
        logger.info('Timeout threshold {}'.format(job.timeout))

        if status == 'success':
            logger.info('The job returned: {}'.format(result))
            assert exception is None
            assert traceback is None

        elif status == 'timeout':
            logger.info('The job took too long and timed out')
            assert result is None
            assert exception is None
            assert traceback is None

        elif status == 'failure':
            logger.info('The job raised an exception on runtime')
            assert result is None
            assert exception is not None
            assert traceback is not None


Once the callback is defined, it can be passed in during initialization:

.. code-block:: python

    from kq import Worker
    from my_module import callback

    worker = Worker(
        hosts='host:7000,host:8000',
        callback=callback,  # pass in the callback
    )
    # The worker will automatically invoke the callback
    worker.start()


When using the :ref:`KQ command line tool <command-line-tool>`, the path to
Python module with the callback function definition can be provided instead:

.. code-block:: bash

    ~$ kq worker --verbose --callback=/my/module/with/callback/function

    [INFO] Starting Worker(topic=default) ...
    [INFO] Processing Record(topic=default, partition=5, offset=3) ...
    [INFO] Running Job 1b92xle0: my_module.my_func(1, 2, baz=3) ...
    [INFO] Job 1b92xle0 returned: (1, 2, 3)
    [INFO] Executing callback ...

The module must contain a function named ``callback`` with the correct
signature.
