import logging

import dill
from kafka import KafkaConsumer

from kq import Job, Message, Worker

# Set up logging
formatter = logging.Formatter(
    fmt="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger("kq.worker")
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def callback(status, message, job, result, exception, stacktrace):
    """Example callback function.

    :param status: Job status. Possible values are "invalid" (job could not be
        deserialized or was malformed), "failure" (job raised an exception),
        "timeout" (job timed out), or "success" (job finished successfully and
        returned a result).
    :type status: str
    :param message: Kafka message.
    :type message: kq.Message
    :param job: Job object, or None if **status** was "invalid".
    :type job: kq.Job
    :param result: Job result, or None if an exception was raised.
    :type result: object | None
    :param exception: Exception raised by job, or None if there was none.
    :type exception: Exception | None
    :param stacktrace: Exception traceback, or None if there was none.
    :type stacktrace: str | None
    """
    assert status in ["invalid", "success", "timeout", "failure"]
    assert isinstance(message, Message)

    if status == "invalid":
        assert job is None
        assert result is None
        assert exception is None
        assert stacktrace is None

    if status == "success":
        assert isinstance(job, Job)
        assert exception is None
        assert stacktrace is None

    elif status == "timeout":
        assert isinstance(job, Job)
        assert result is None
        assert exception is None
        assert stacktrace is None

    elif status == "failure":
        assert isinstance(job, Job)
        assert result is None
        assert exception is not None
        assert stacktrace is not None


def deserializer(serialized):
    """Example deserializer function with extra sanity checking.

    :param serialized: Serialized byte string.
    :type serialized: bytes
    :return: Deserialized job object.
    :rtype: kq.Job
    """
    assert isinstance(serialized, bytes), "Expecting a bytes"
    return dill.loads(serialized)


if __name__ == "__main__":
    consumer = KafkaConsumer(
        bootstrap_servers="127.0.0.1:9092",
        group_id="group",
        enable_auto_commit=True,
        auto_offset_reset="latest",
    )
    worker = Worker(
        topic="topic", consumer=consumer, callback=callback, deserializer=deserializer
    )
    worker.start()
