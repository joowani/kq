import _thread
import logging
import threading
import traceback
from typing import Any, Callable, Optional

import dill
from kafka import KafkaConsumer

from kq.job import Job
from kq.message import Message
from kq.utils import get_call_repr, is_none_or_func, is_none_or_logger, is_str


class Worker:
    """Fetches :doc:`jobs <job>` from Kafka topics and processes them.

    :param topic: Name of the Kafka topic.
    :type topic: str
    :param consumer: Kafka consumer instance with a group ID (required). For
        more details on consumers, refer to kafka-python's documentation_.
    :type consumer: kafka.KafkaConsumer_
    :param callback: Callback function which is executed every time a job is
        processed. See :doc:`here <callback>` for more details.
    :type callback: callable
    :param deserializer: Callable which takes a byte string and returns a
        deserialized :doc:`job <job>` namedtuple. If not set, ``dill.loads``
        is used by default. See :doc:`here <serializer>` for more details.
    :type deserializer: callable
    :param logger: Logger for recording worker activities. If not set, logger
        named ``kq.worker`` is used with default settings (you need to define
        your own formatters and handlers). See :doc:`here <logging>` for more
        details.
    :type logger: logging.Logger

    **Example:**

    .. code-block:: python

        from kafka import KafkaConsumer
        from kq import Worker

        # Set up a Kafka consumer. Group ID is required.
        consumer = KafkaConsumer(
            bootstrap_servers='127.0.0.1:9092',
            group_id='group'
        )

        # Set up a worker.
        worker = Worker(topic='topic', consumer=consumer)

        # Start the worker to process jobs.
        worker.start()

    .. _documentation:
        http://kafka-python.rtfd.io/en/master/#kafkaconsumer
    .. _kafka.KafkaConsumer:
        http://kafka-python.rtfd.io/en/master/apidoc/KafkaConsumer.html
    """

    def __init__(
        self,
        topic: str,
        consumer: KafkaConsumer,
        callback: Optional[Callable[..., Any]] = None,
        deserializer: Optional[Callable[[bytes], Any]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        assert is_str(topic), "topic must be a str"
        assert isinstance(consumer, KafkaConsumer), "bad consumer instance"
        assert consumer.config["group_id"], "consumer must have group_id"
        assert is_none_or_func(callback), "callback must be a callable"
        assert is_none_or_func(deserializer), "deserializer must be a callable"
        assert is_none_or_logger(logger), "bad logger instance"

        self._topic = topic
        self._hosts: str = consumer.config["bootstrap_servers"]
        self._group: str = consumer.config["group_id"]
        self._consumer = consumer
        self._callback = callback
        self._deserializer = deserializer or dill.loads
        self._logger = logger or logging.getLogger("kq.worker")

    def __repr__(self) -> str:
        """Return the string representation of the worker.

        :return: String representation of the worker.
        :rtype: str
        """
        return f"Worker(hosts={self._hosts}, topic={self._topic}, group={self._group})"

    def __del__(self) -> None:  # pragma: no cover
        # noinspection PyBroadException
        try:
            self._consumer.close()
        except Exception:
            pass

    def _execute_callback(
        self,
        status: str,
        message: Message,
        job: Optional[Job],
        res: Any,
        err: Optional[Exception],
        stacktrace: Optional[str],
    ) -> None:
        """Execute the callback.

        :param status: Job status. Possible values are "invalid" (job could not
            be deserialized or was malformed), "failure" (job raised an error),
            "timeout" (job timed out), or "success" (job finished successfully
            and returned a result).
        :type status: str
        :param message: Kafka message.
        :type message: :doc:`kq.Message <message>`
        :param job: Job object, or None if **status** was "invalid".
        :type job: kq.Job
        :param res: Job result, or None if an exception was raised.
        :type res: object | None
        :param err: Exception raised by job, or None if there was none.
        :type err: Exception | None
        :param stacktrace: Exception traceback, or None if there was none.
        :type stacktrace: str | None
        """
        if self._callback is not None:
            try:
                self._logger.info("Executing callback ...")
                self._callback(status, message, job, res, err, stacktrace)
            except Exception as err:
                self._logger.exception(f"Callback raised an exception: {err}")

    def _process_message(self, msg: Message) -> None:
        """De-serialize the message and execute the job.

        :param msg: Kafka message.
        :type msg: :doc:`kq.Message <message>`
        """
        self._logger.info(
            "Processing Message(topic={}, partition={}, offset={}) ...".format(
                msg.topic, msg.partition, msg.offset
            )
        )
        try:
            job = self._deserializer(msg.value)
            job_repr = get_call_repr(job.func, *job.args, **job.kwargs)

        except Exception as err:
            self._logger.exception(f"Job was invalid: {err}")
            self._execute_callback("invalid", msg, None, None, None, None)
        else:
            self._logger.info(f"Executing job {job.id}: {job_repr}")

            timer: Optional[threading.Timer]
            if job.timeout:
                timer = threading.Timer(job.timeout, _thread.interrupt_main)
                timer.start()
            else:
                timer = None
            try:
                res = job.func(*job.args, **job.kwargs)
            except KeyboardInterrupt:
                self._logger.error(f"Job {job.id} timed out or was interrupted")
                self._execute_callback("timeout", msg, job, None, None, None)
            except Exception as err:
                self._logger.exception(f"Job {job.id} raised an exception:")
                tb = traceback.format_exc()
                self._execute_callback("failure", msg, job, None, err, tb)
            else:
                self._logger.info(f"Job {job.id} returned: {res}")
                self._execute_callback("success", msg, job, res, None, None)
            finally:
                if timer is not None:
                    timer.cancel()

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
    def group(self) -> str:
        """Return the Kafka consumer group ID.

        :return: Kafka consumer group ID.
        :rtype: str
        """
        return self._group

    @property
    def consumer(self) -> KafkaConsumer:
        """Return the Kafka consumer instance.

        :return: Kafka consumer instance.
        :rtype: kafka.KafkaConsumer
        """
        return self._consumer

    @property
    def deserializer(self) -> Callable[[bytes], Any]:
        """Return the deserializer function.

        :return: Deserializer function.
        :rtype: callable
        """
        return self._deserializer

    @property
    def callback(self) -> Optional[Callable[..., Any]]:
        """Return the callback function.

        :return: Callback function, or None if not set.
        :rtype: callable | None
        """
        return self._callback

    def start(
        self, max_messages: Optional[int] = None, commit_offsets: bool = True
    ) -> int:
        """Start processing Kafka messages and executing jobs.

        :param max_messages: Maximum number of Kafka messages to process before
            stopping. If not set, worker runs until interrupted.
        :type max_messages: int | None
        :param commit_offsets: If set to True, consumer offsets are committed
            every time a message is processed (default: True).
        :type commit_offsets: bool
        :return: Total number of messages processed.
        :rtype: int
        """
        self._logger.info(f"Starting {self} ...")

        self._consumer.unsubscribe()
        self._consumer.subscribe([self.topic])

        messages_processed = 0
        while max_messages is None or messages_processed < max_messages:
            record = next(self._consumer)

            message = Message(
                topic=record.topic,
                partition=record.partition,
                offset=record.offset,
                key=record.key,
                value=record.value,
            )
            self._process_message(message)

            if commit_offsets:
                self._consumer.commit()

            messages_processed += 1

        return messages_processed
