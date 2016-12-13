from __future__ import absolute_import, print_function, unicode_literals

import collections
import logging
import multiprocessing as mp
import traceback as tb

import dill
import kafka

from kq.job import Job
from kq.utils import func_repr, rec_repr


class Worker(object):
    """KQ worker.

    A worker fetches jobs from a Kafka broker, de-serializes them and
    executes them asynchronously in the background. Here is an example
    of initializing and starting a worker:

    .. code-block:: python

        from kq import Worker

        worker = Worker(
            hosts='host:7000,host:8000',
            topic='foo',
            timeout=3600,
            callback=None,
            job_size=10000000,
            cafile='/my/files/cafile',
            certfile='/my/files/certfile',
            keyfile='/my/files/keyfile',
            crlfile='/my/files/crlfile'
        )
        worker.start()

    .. note::

        The number of partitions in a Kafka topic limits how many workers
        can read from the queue in parallel. For example, maximum of 10
        workers can work off a queue with 10 partitions.

    :param hosts: Comma-separated Kafka hostnames and ports. For example,
        ``"localhost:9000,localhost:8000,192.168.1.1:7000"`` is a valid
        input string. Default: ``"127.0.0.1:9092"``.
    :type hosts: str | unicode
    :param topic: Name of the Kafka topic. Default: ``"default"``.
    :type topic: str | unicode
    :param timeout: Default job timeout threshold in seconds. If not set, the
        enqueued jobs are left to run until they finish. This means a hanging
        job can potentially block the workers. Default: ``None`` (no timeout).
        If set, overrides timeouts set when the jobs were first enqueued.
    :type timeout: int
    :param callback: Function executed after a job is fetched and processed.
        Its signature must be ``callback(status, job, exception, traceback)``
        where:

        .. code-block:: none

            status (str | unicode)
                The status of the job execution, which can be "timeout",
                "failure" or "success".

            job (kq.job.Job)
                The job namedtuple object consumed by the worker.

            result (object)
                The result of the job execution.

            exception (Exception | None)
                The exception raised while the job was running, or None
                if there were no errors.

            traceback (str | unicode | None)
                The traceback of the exception raised while the job was
                running, or None if there were no errors.

    :type callback: callable
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
                 callback=None,
                 job_size=1048576,
                 cafile=None,
                 certfile=None,
                 keyfile=None,
                 crlfile=None):
        self._hosts = hosts
        self._topic = topic
        self._timeout = timeout
        self._callback = callback
        self._pool = None
        self._logger = logging.getLogger('kq')
        self._consumer = kafka.KafkaConsumer(
            self._topic,
            group_id=self._topic,
            bootstrap_servers=self._hosts,
            max_partition_fetch_bytes=job_size * 2,
            ssl_cafile=cafile,
            ssl_certfile=certfile,
            ssl_keyfile=keyfile,
            ssl_crlfile=crlfile,
            consumer_timeout_ms=-1,
            enable_auto_commit=False,
            auto_offset_reset='latest',
        )

    def __del__(self):
        """Commit the Kafka consumer offsets and close the consumer."""
        if hasattr(self, '_consumer'):
            try:
                self._logger.info('Closing consumer ...')
                self._consumer.close()
            except Exception as e:  # pragma: no cover
                self._logger.warning('Failed to close consumer: {}'.format(e))

    def __repr__(self):
        """Return a string representation of the worker.

        :return: string representation of the worker
        :rtype: str | unicode
        """
        return 'Worker(topic={})'.format(self._topic)

    def _exec_callback(self, status, job, result, exception, traceback):
        """Execute the callback in a try-except block.

        :param status: The status of the job consumption. Possible values are
            ``timeout', ``failure`` and ``success``.
        :type status: str | unicode
        :param job: The job consumed by the worker
        :type job: kq.job.Job
        :param result: The result of the job execution.
        :type result: object
        :param exception: Exception raised while the job was running (i.e.
            status was ``failure``), or ``None`` if there were no errors
            (i.e. status was ``success``).
        :type exception: Exception | None
        :param traceback: The stacktrace of the exception (i.e. status was
            ``failure``) was running or ``None`` if there were no errors.
        :type traceback: str | unicode | None
        """
        if self._callback is not None:
            try:
                self._logger.info('Executing callback ...')
                self._callback(status, job, result, exception, traceback)
            except Exception as e:
                self._logger.exception('Callback failed: {}'.format(e))

    def _consume_record(self, record):
        """De-serialize the message and execute the incoming job.

        :param record: Record fetched from the Kafka topic.
        :type record: kafka.consumer.fetcher.ConsumerRecord
        """
        rec = rec_repr(record)
        self._logger.info('Processing {} ...'.format(rec))
        try:
            job = dill.loads(record.value)
        except:
            self._logger.warning('{} unloadable. Skipping ...'.format(rec))
        else:
            # Simple check for job validity
            if not (isinstance(job, Job)
                    and isinstance(job.args, collections.Iterable)
                    and isinstance(job.kwargs, collections.Mapping)
                    and callable(job.func)):
                self._logger.warning('{} malformed. Skipping ...'.format(rec))
                return
            func, args, kwargs = job.func, job.args, job.kwargs
            self._logger.info('Running Job {}: {} ...'.format(
                job.id, func_repr(func, args, kwargs)
            ))
            try:
                timeout = self._timeout or job.timeout
                if timeout is None:
                    res = func(*args, **kwargs)
                else:
                    run = self._pool.apply_async(func, args, kwargs)
                    res = run.get(timeout)
            except mp.TimeoutError:
                self._logger.error('Job {} timed out after {} seconds.'
                                   .format(job.id, job.timeout))
                self._exec_callback('timeout', job, None, None, None)
            except Exception as e:
                self._logger.exception('Job {} failed: {}'.format(job.id, e))
                self._exec_callback('failure', job, None, e, tb.format_exc())
            else:
                self._logger.info('Job {} returned: {}'.format(job.id, res))
                self._exec_callback('success', job, res, None, None)

    @property
    def consumer(self):
        """Return the Kafka consumer object.

        :return: Kafka consumer object.
        :rtype: kafka.consumer.KafkaConsumer
        """
        return self._consumer

    @property
    def hosts(self):
        """Return the list of Kafka host names and ports.

        :return: list of Kafka host names and ports
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

    def start(self):
        """Start fetching and processing enqueued jobs in the topic.

        Once started, the worker will continuously poll the Kafka broker in
        a loop until jobs are available in the topic partitions. The loop is
        only stopped via external triggers (e.g. keyboard interrupts).
        """
        self._logger.info('Starting {} ...'.format(self))
        self._pool = mp.Pool(processes=1)
        try:
            for record in self._consumer:
                self._consume_record(record)
                self._consumer.commit()
        except KeyboardInterrupt:  # pragma: no cover
            self._logger.info('Stopping {} ...'.format(self))
            self._pool.terminate()  # TODO not sure if necessary
