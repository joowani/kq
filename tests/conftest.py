import logging
import os
import time
import uuid

import dill
import pytest
from kafka import KafkaConsumer, KafkaProducer

from kq import Job, Message, Queue, Worker

test_dir = os.getcwd()
if not test_dir.endswith("tests"):
    test_dir = os.path.join(test_dir, "tests")
log_file = os.path.join(test_dir, "output.log")

handler = logging.FileHandler(log_file, mode="w")
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

queue_logger = logging.getLogger("kq.queue")
queue_logger.setLevel(logging.DEBUG)
queue_logger.addHandler(handler)

worker_logger = logging.getLogger("kq.worker")
worker_logger.setLevel(logging.DEBUG)
worker_logger.addHandler(handler)


def success_function(a, b):
    """Function which completes successfully."""
    return a * b


def failure_function(a, b):
    """Function which raises an exception."""
    raise ValueError(a + b)


def timeout_function(a, b):
    """Function which runs forever and times out."""
    while True:
        assert a + b > 0


# noinspection PyMethodMayBeStatic
class Callable(object):  # pragma: no covers

    unbound_method = success_function

    def __call__(self, a, b):
        return a * b

    @staticmethod
    def static_method(a, b):
        return a * b

    def instance_method(self, a, b):
        return a * b


class Callback(object):
    """Callback which can be set to succeed or fail."""

    def __init__(self):
        self.logger = logging.getLogger("kq.worker")
        self.succeed = True

    def __call__(self, status, message, job, result, exception, stacktrace):
        if not self.succeed:
            raise RuntimeError

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

        self.logger.info(f'Callback got job status "{status}"')


class Deserializer(object):
    """Deserializer which can be set to succeed or fail."""

    def __init__(self):
        self.succeed = True

    def __call__(self, job):
        if not self.succeed:
            raise RuntimeError
        return dill.loads(job)


class LogAccessor(object):
    """KQ log accessor."""

    @property
    def lines(self):
        time.sleep(0.5)
        with open(log_file, "r") as fp:
            lines = fp.read().splitlines()
        return [line for line in lines if line.startswith("[")]

    @property
    def last_line(self):
        return self.lines[-1]

    def last_lines(self, line_count=1):
        return iter(self.lines[-line_count:])


def pytest_addoption(parser):
    parser.addoption("--host", action="store", default="127.0.0.1")
    parser.addoption("--port", action="store", default="9092")


@pytest.fixture(scope="session", autouse=False)
def func():
    return success_function


@pytest.fixture(scope="session", autouse=False)
def success_func():
    return success_function


@pytest.fixture(scope="session", autouse=False)
def failure_func():
    return failure_function


@pytest.fixture(scope="session", autouse=False)
def timeout_func():
    return timeout_function


@pytest.fixture(scope="session", autouse=False)
def callable_cls():
    return Callable


@pytest.fixture(scope="session", autouse=False)
def log():
    return LogAccessor()


@pytest.fixture(scope="session", autouse=False)
def callback():
    return Callback()


@pytest.fixture(scope="session", autouse=False)
def deserializer():
    return Deserializer()


@pytest.fixture(scope="session", autouse=False)
def hosts(pytestconfig):
    host = pytestconfig.getoption("host")
    port = pytestconfig.getoption("port")
    return host + ":" + port


@pytest.fixture(scope="module", autouse=False)
def topic():
    return uuid.uuid4().hex


@pytest.fixture(scope="module", autouse=False)
def group():
    return uuid.uuid4().hex


# noinspection PyShadowingNames
@pytest.fixture(scope="module", autouse=False)
def producer(hosts):
    return KafkaProducer(bootstrap_servers=hosts)


# noinspection PyShadowingNames
@pytest.fixture(scope="module", autouse=False)
def consumer(hosts, group):
    return KafkaConsumer(
        bootstrap_servers=hosts,
        group_id=group,
        auto_offset_reset="earliest",
    )


# noinspection PyShadowingNames
@pytest.fixture(scope="module", autouse=False)
def queue(topic, producer):
    return Queue(topic, producer)


# noinspection PyShadowingNames
@pytest.fixture(scope="module", autouse=False)
def worker(topic, consumer, callback, deserializer):
    return Worker(topic, consumer, callback, deserializer)


# noinspection PyShadowingNames
@pytest.fixture(scope="function", autouse=True)
def before(callback, deserializer):
    callback.succeed = True
    deserializer.succeed = True
