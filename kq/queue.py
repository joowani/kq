import logging
import time
import uuid
from typing import Any, Callable, Optional, Union

import dill
from kafka import KafkaProducer

from kq.job import Job
from kq.utils import (
    is_dict,
    is_none_or_bytes,
    is_none_or_func,
    is_none_or_int,
    is_none_or_logger,
    is_number,
    is_seq,
    is_str,
)


class EnqueueSpec:
    __slots__ = [
        "_topic",
        "_producer",
        "_serializer",
        "_logger",
        "_timeout",
        "_key",
        "_partition",
        "delay",
    ]

    def __init__(
        self,
        topic: str,
        producer: KafkaProducer,
        serializer: Callable[[Any], bytes],
        logger: logging.Logger,
        timeout: Union[float, int],
        key: Optional[bytes],
        partition: Optional[int],
    ):
        assert is_number(timeout), "timeout must be an int or float"
        assert is_none_or_bytes(key), "key must be a bytes"
        assert is_none_or_int(partition), "partition must be an int"

        self._topic = topic
        self._producer = producer
        self._serializer = serializer
        self._logger = logger
        self._timeout = timeout
        self._key = key
        self._partition = partition

    def enqueue(
        self, obj: Union[Callable[..., Any], Job], *args: Any, **kwargs: Any
    ) -> Job:
        """Enqueue a function call or :doc:`job` instance.

        :param obj: Function or :doc:`job <job>`. Must be serializable and
            importable by :doc:`worker <worker>` processes.
        :type obj: callable | :doc:`kq.Job <job>`
        :param args: Positional arguments for the function. Ignored if **func**
            is a :doc:`job <job>` object.
        :param kwargs: Keyword arguments for the function. Ignored if **func**
            is a :doc:`job <job>` object.
        :return: Enqueued job.
        :rtype: :doc:`kq.Job <job>`
        """
        timestamp = int(time.time() * 1000)

        if isinstance(obj, Job):
            if obj.id is None:
                job_id = uuid.uuid4().hex
            else:
                assert is_str(obj.id), "Job.id must be a str"
                job_id = obj.id

            if obj.args is None:
                args = tuple()
            else:
                assert is_seq(obj.args), "Job.args must be a list or tuple"
                args = tuple(obj.args)

            assert callable(obj.func), "Job.func must be a callable"

            func = obj.func
            kwargs = {} if obj.kwargs is None else obj.kwargs
            timeout = self._timeout if obj.timeout is None else obj.timeout
            key = self._key if obj.key is None else obj.key
            part = self._partition if obj.partition is None else obj.partition

            assert is_dict(kwargs), "Job.kwargs must be a dict"
            assert is_number(timeout), "Job.timeout must be an int or float"
            assert is_none_or_bytes(key), "Job.key must be a bytes"
            assert is_none_or_int(part), "Job.partition must be an int"
        else:
            assert callable(obj), "first argument must be a callable"
            job_id = uuid.uuid4().hex
            func = obj
            args = args
            kwargs = kwargs
            timeout = self._timeout
            key = self._key
            part = self._partition

        job = Job(
            id=job_id,
            timestamp=timestamp,
            topic=self._topic,
            func=func,
            args=args,
            kwargs=kwargs,
            timeout=timeout,
            key=key,
            partition=part,
        )
        self._logger.info(f"Enqueueing {job} ...")
        self._producer.send(
            self._topic,
            value=self._serializer(job),
            key=self._serializer(key) if key else None,
            partition=part,
            timestamp_ms=timestamp,
        )
        self._producer.flush()
        return job


class Queue:
    """Enqueues function calls in Kafka topics as :doc:`jobs <job>`.

    :param topic: Name of the Kafka topic.
    :type topic: str
    :param producer: Kafka producer instance. For more details on producers,
        refer to kafka-python's `documentation
        <http://kafka-python.rtfd.io/en/master/#kafkaproducer>`_.
    :type producer: kafka.KafkaProducer_
    :param serializer: Callable which takes a :doc:`job <job>` namedtuple and
        returns a serialized byte string. If not set, ``dill.dumps`` is used
        by default. See :doc:`here <serializer>` for more details.
    :type serializer: callable
    :param timeout: Default job timeout threshold in seconds. If left at 0
        (default), jobs run until completion. This value can be overridden
        when enqueueing jobs.
    :type timeout: int | float
    :param logger: Logger for recording queue activities. If not set, logger
        named ``kq.queue`` is used with default settings (you need to define
        your own formatters and handlers). See :doc:`here <logging>` for more
        details.
    :type logger: logging.Logger

    **Example:**

    .. testcode::

        import requests

        from kafka import KafkaProducer
        from kq import Queue

        # Set up a Kafka producer.
        producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

        # Set up a queue.
        queue = Queue(topic='topic', producer=producer, timeout=3600)

        # Enqueue a function call.
        job = queue.enqueue(requests.get, 'https://www.google.com/')

    .. _kafka.KafkaProducer:
        http://kafka-python.rtfd.io/en/master/apidoc/KafkaProducer.html
    """

    def __init__(
        self,
        topic: str,
        producer: KafkaProducer,
        serializer: Optional[Callable[..., bytes]] = None,
        timeout: int = 0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        assert is_str(topic), "topic must be a str"
        assert isinstance(producer, KafkaProducer), "bad producer instance"
        assert is_none_or_func(serializer), "serializer must be a callable"
        assert is_number(timeout), "timeout must be an int or float"
        assert timeout >= 0, "timeout must be 0 or greater"
        assert is_none_or_logger(logger), "bad logger instance"

        self._topic = topic
        self._hosts: str = producer.config["bootstrap_servers"]
        self._producer = producer
        self._serializer = serializer or dill.dumps
        self._timeout = timeout
        self._logger = logger or logging.getLogger("kq.queue")
        self._default_enqueue_spec = EnqueueSpec(
            topic=self._topic,
            producer=self._producer,
            serializer=self._serializer,
            logger=self._logger,
            timeout=self._timeout,
            key=None,
            partition=None,
        )

    def __repr__(self) -> str:
        """Return the string representation of the queue.

        :return: String representation of the queue.
        :rtype: str
        """
        return f"Queue(hosts={self._hosts}, topic={self._topic})"

    def __del__(self) -> None:  # pragma: no cover
        # noinspection PyBroadException
        try:
            self._producer.close()
        except Exception:
            pass

    @property
    def hosts(self) -> str:
        """Return comma-separated Kafka hosts and ports string.

        :return: Comma-separated Kafka hosts and ports.
        :rtype: str
        """
        return self._hosts

    @property
    def topic(self) -> str:
        """Return the name of the Kafka topic.

        :return: Name of the Kafka topic.
        :rtype: str
        """
        return self._topic

    @property
    def producer(self) -> KafkaProducer:
        """Return the Kafka producer instance.

        :return: Kafka producer instance.
        :rtype: kafka.KafkaProducer
        """
        return self._producer

    @property
    def serializer(self) -> Callable[..., bytes]:
        """Return the serializer function.

        :return: Serializer function.
        :rtype: callable
        """
        return self._serializer

    @property
    def timeout(self) -> Union[float, int]:
        """Return the default job timeout threshold in seconds.

        :return: Default job timeout threshold in seconds.
        :rtype: float | int
        """
        return self._timeout

    def enqueue(self, func: Callable[..., bytes], *args: Any, **kwargs: Any) -> Job:
        """Enqueue a function call or a :doc:`job <job>`.

        :param func: Function or a :doc:`job <job>` object. Must be
            serializable and available to :doc:`workers <worker>`.
        :type func: callable | :doc:`kq.Job <job>`
        :param args: Positional arguments for the function. Ignored if **func**
            is a :doc:`job <job>` object.
        :param kwargs: Keyword arguments for the function. Ignored if **func**
            is a :doc:`job <job>` object.
        :return: Enqueued job.
        :rtype: :doc:`kq.Job <job>`

        **Example:**

        .. testcode::

            import requests

            from kafka import KafkaProducer
            from kq import  Job, Queue

            # Set up a Kafka producer.
            producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

            # Set up a queue.
            queue = Queue(topic='topic', producer=producer)

            # Enqueue a function call.
            queue.enqueue(requests.get, 'https://www.google.com/')

            # Enqueue a job object.
            job = Job(func=requests.get, args=['https://www.google.com/'])
            queue.enqueue(job)

        .. note::

            The following rules apply when enqueueing a :doc:`job <job>`:

            * If ``Job.id`` is not set, a random one is generated.
            * If ``Job.timestamp`` is set, it is replaced with current time.
            * If ``Job.topic`` is set, it is replaced with current topic.
            * If ``Job.timeout`` is set, its value overrides others.
            * If ``Job.key`` is set, its value overrides others.
            * If ``Job.partition`` is set, its value overrides others.

        """
        return self._default_enqueue_spec.enqueue(func, *args, **kwargs)

    def using(
        self,
        timeout: Optional[Union[float, int]] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
    ) -> EnqueueSpec:
        """Set enqueue specifications such as timeout, key and partition.

        :param timeout: Job timeout threshold in seconds. If not set, default
            timeout (specified during queue initialization) is used instead.
        :type timeout: int | float
        :param key: Kafka message key. Jobs with the same keys are sent to the
            same topic partition and executed sequentially. Applies only if the
            **partition** parameter is not set, and the producer’s partitioner
            configuration is left as default. For more details on producers,
            refer to kafka-python's documentation_.
        :type key: bytes
        :param partition: Topic partition the message is sent to. If not set,
            the producer's partitioner selects the partition. For more details
            on producers, refer to kafka-python's documentation_.
        :type partition: int
        :return: Enqueue specification object which has an ``enqueue`` method
            with the same signature as :func:`kq.queue.Queue.enqueue`.
        :rtype: EnqueueSpec

        **Example:**

        .. testcode::

            import requests

            from kafka import KafkaProducer
            from kq import Job, Queue

            # Set up a Kafka producer.
            producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

            # Set up a queue.
            queue = Queue(topic='topic', producer=producer)

            url = 'https://www.google.com/'

            # Enqueue a function call in partition 0 with message key 'foo'.
            queue.using(partition=0, key=b'foo').enqueue(requests.get, url)

            # Enqueue a function call with a timeout of 10 seconds.
            queue.using(timeout=10).enqueue(requests.get, url)

            # Job values are preferred over values set with "using" method.
            job = Job(func=requests.get, args=[url], timeout=5)
            queue.using(timeout=10).enqueue(job)  # timeout is still 5

        .. _documentation: http://kafka-python.rtfd.io/en/master/#kafkaproducer
        """
        return EnqueueSpec(
            topic=self._topic,
            producer=self._producer,
            serializer=self._serializer,
            logger=self._logger,
            timeout=timeout or self._timeout,
            key=key,
            partition=partition,
        )
