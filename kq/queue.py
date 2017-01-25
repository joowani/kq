from __future__ import absolute_import, print_function, unicode_literals

import functools
import logging
import time
import uuid

import dill
import kafka
from kafka.errors import KafkaError

from kq.job import Job


class Queue(object):
    """KQ queue.

    A queue serializes incoming function calls and places them into a Kafka
    topic as *jobs*. Workers fetch these jobs and execute them asynchronously
    in the background. Here is an example of initializing and using a queue:

    .. code-block:: python

        from kq import Queue, Job

        queue = Queue(
            hosts='host:7000,host:8000',
            topic='foo',
            timeout=3600,
            compression='gzip',
            acks=0,
            retries=5,
            job_size=10000000,
            cafile='/my/files/cafile',
            certfile='/my/files/certfile',
            keyfile='/my/files/keyfile',
            crlfile='/my/files/crlfile'
        )
        job = queue.enqueue(my_func, *args, **kwargs)
        assert isinstance(job, Job)

    .. note::

        The number of partitions in a Kafka topic limits how many workers
        can read from the queue in parallel. For example, maximum of 10
        workers can work off a queue with 10 partitions.


    :param hosts: Comma-separated Kafka hostnames and ports. For example,
        ``"localhost:9000,localhost:8000,192.168.1.1:7000"`` is a valid input
        string. Default: ``"127.0.0.1:9092"``.
    :type hosts: str | unicode
    :param topic: Name of the Kafka topic. Default: ``"default"``.
    :type topic: str | unicode
    :param timeout: Default job timeout threshold in seconds. If not set, the
        enqueued jobs are left to run until they finish. This means a hanging
        job can potentially block the workers. Default: ``None`` (no timeout).
    :type timeout: int
    :param compression: The algorithm used for compressing job data. Allowed
        values are: ``"gzip"``, ``"snappy"`` and ``"lz4"``. Default: ``None``
        (no compression).
    :type compression: str | unicode
    :param acks: The number of acknowledgements required from the broker(s)
        before considering a job successfully enqueued. Allowed values are:

        .. code-block:: none

            0: Do not wait for any acknowledgment from the broker leader
               and consider the job enqueued as soon as it is added to
               the socket buffer. Persistence is not guaranteed on broker
               failures.

            1: Wait for the job to be saved on the broker leader but not
               for it be replicated across other brokers. If the leader
               broker fails before the replication finishes the job may
               not be persisted.

           -1: Wait for the job to be replicated across all brokers. As
               long as one of the brokers is functional job persistence
               is guaranteed.

        Default: ``1``.

    :type acks: int
    :param retries: The maximum number of attempts to re-enqueue a job when
        the job fails to reach the broker. Retries may alter the sequence of
        the enqueued jobs. Default: ``0``.
    :type retries: int
    :param job_size: The max size of each job in bytes. Default: ``1048576``.
    :type job_size: int
    :param cafile: Full path to the trusted CA certificate file.
    :type cafile: str | unicode
    :param certfile: Full path to the client certificate file.
    :type certfile: str | unicode
    :param keyfile: Full path to the client private key file.
    :type keyfile: str | unicode
    :param crlfile: Full path to the CRL file for validating certification
        expiry. This option is only available with Python 3.4+ or 2.7.9+.
    :type crlfile: str | unicode
    """

    def __init__(self,
                 hosts='127.0.0.1:9092',
                 topic='default',
                 timeout=None,
                 compression=None,
                 acks=1,
                 retries=0,
                 job_size=1048576,
                 cafile=None,
                 certfile=None,
                 keyfile=None,
                 crlfile=None):
        self._hosts = hosts
        self._topic = topic
        self._timeout = timeout
        self._logger = logging.getLogger('kq')
        self._producer = kafka.KafkaProducer(
            bootstrap_servers=self._hosts,
            compression_type=compression,
            acks=acks,
            retries=retries,
            max_request_size=job_size,
            buffer_memory=max(job_size, 33554432),
            ssl_cafile=cafile,
            ssl_certfile=certfile,
            ssl_keyfile=keyfile,
            ssl_crlfile=crlfile
        )

    def __repr__(self):
        """Return a string representation of the queue.

        :return: String representation of the queue.
        :rtype: str | unicode
        """
        return 'Queue(topic={})'.format(self._topic)

    @property
    def producer(self):
        """Return the Kafka producer object.

        :return: Kafka producer object.
        :rtype: kafka.producer.KafkaProducer
        """
        return self._producer

    @property
    def hosts(self):
        """Return the list of Kafka host names and ports.

        :return: List of Kafka host names and ports.
        :rtype: [str]
        """
        return self._hosts.split(',')

    @property
    def topic(self):
        """Return the name of the Kafka topic in use.

        :return: Name of the Kafka topic in use.
        :rtype: str | unicode
        """
        return self._topic

    @property
    def timeout(self):
        """Return the job timeout threshold in seconds.

        :return: Job timeout threshold in seconds.
        :rtype: int
        """
        return self._timeout

    def enqueue(self, obj, *args, **kwargs):
        """Place the function call (or the job) in the Kafka topic.

        For example:

        .. code-block:: python

            import requests
            from kq import Queue

            q = Queue()

            # You can queue the function call with its arguments
            job = q.enqueue(requests.get, 'https://www.google.com')

            # Or you can queue a kq.job.Job instance directly
            q.enqueue(job)

        :param obj: Function or the job object to enqueue. If a function is
            given, the function *must* be pickle-able.
        :type obj: callable | kq.job.Job
        :param args: Arguments for the function. Ignored if a KQ job object
            is given for the first argument instead.
        :type args: list
        :param kwargs: Keyword arguments for the function. Ignored if a KQ
            job instance is given as the first argument instead.
        :type kwargs: dict
        :return: The job that was enqueued
        :rtype: kq.job.Job
        """
        if isinstance(obj, Job):
            func = obj.func
            args = obj.args
            kwargs = obj.kwargs
            key = obj.key
        else:
            func = obj
            key = None

        if not callable(func):
            raise ValueError('{} is not a callable'.format(func))

        job = Job(
            id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            topic=self._topic,
            func=func,
            args=args,
            kwargs=kwargs,
            timeout=self._timeout,
            key=key
        )
        future = self._producer.send(self._topic, dill.dumps(job), key=key)
        try:
            future.get(timeout=self._timeout or 5)
        except KafkaError as e:
            self._logger.exception('Queuing failed: {}'.format(e.message))
            return None
        self._logger.info('Enqueued: {}'.format(job))
        return job

    def enqueue_with_key(self, key, obj, *args, **kwargs):
        """Place the function call (or the job) in the Kafka topic with key.

        For example:

        .. code-block:: python

            import requests
            from kq import Queue

            q = Queue()

            url = 'https://www.google.com'

            # You can queue the function call with its arguments
            job = q.enqueue_with_key('my_key', requests.get, url)

            # Or you can queue a kq.job.Job instance directly
            q.enqueue_with_key('my_key', job)

        :param key: The key for the Kafka message. Jobs with the same key are
            guaranteed to be placed in the same Kafka partition and processed
            sequentially. If a job object is enqueued, its key is overwritten.
        :type key: str
        :param obj: Function or the job object to enqueue. If a function is
            given, the function *must* be pickle-able.
        :type obj: callable | kq.job.Job
        :param args: Arguments for the function. Ignored if a KQ job object
            is given for the first argument instead.
        :type args: list
        :param kwargs: Keyword arguments for the function. Ignored if a KQ
            job instance is given as the first argument instead.
        :type kwargs: dict
        :return: The job that was enqueued
        :rtype: kq.job.Job
        """
        if isinstance(obj, Job):
            func = obj.func
            args = obj.args
            kwargs = obj.kwargs
        else:
            func = obj

        if not callable(func):
            raise ValueError('{} is not a callable'.format(func))

        job = Job(
            id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            topic=self._topic,
            func=func,
            args=args,
            kwargs=kwargs,
            timeout=self._timeout,
            key=key
        )
        future = self._producer.send(self._topic, dill.dumps(job), key=key)
        try:
            future.get(timeout=self._timeout or 5)
        except KafkaError as e:
            self._logger.exception('Queuing failed: {}'.format(e.message))
            return None
        self._logger.info('Enqueued: {}'.format(job))
        return job

    def job(self, func):
        """Decorator which add a **delay** method to a function.

        When the **delay** method is called, the function is queued as a job.
        For example:

        .. code-block:: python

            from kq import Queue
            queue = Queue()

            @queue.job
            def calculate_sum(a, b, c):
                return a + b + c

            # Enqueue the function as a job
            calculate_sum.delay(1, 2, 3)

        :param func: The function to decorate.
        :type func: callable
        :return: The decorated function with new method **delay**
        :rtype: callable
        """
        @functools.wraps(func)
        def delay(*args, **kwargs):  # pragma: no cover
            return self.enqueue(func, *args, **kwargs)
        func.delay = delay
        return func

    def flush(self):
        """Force-flush all buffered records to the broker."""
        self._logger.info('Flushing {} ...'.format(self))
        self._producer.flush()
