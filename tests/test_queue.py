import time
import uuid

import pytest
from kafka import KafkaProducer

from kq import Job, Queue


def test_queue_properties(queue, hosts, topic):
    assert hosts in repr(queue)
    assert topic in repr(queue)
    assert queue.producer.config["bootstrap_servers"] == hosts
    assert isinstance(queue.hosts, str) and queue.hosts == hosts
    assert isinstance(queue.topic, str) and queue.topic == topic
    assert isinstance(queue.producer, KafkaProducer)
    assert isinstance(queue.timeout, (int, float))
    assert callable(queue.serializer) or queue.serializer is None


# noinspection PyTypeChecker
def test_queue_initialization_with_bad_args(producer):
    with pytest.raises(AssertionError) as e:
        Queue(topic=True, producer=producer)
    assert str(e.value) == "topic must be a str"

    with pytest.raises(AssertionError) as e:
        Queue(topic="topic", producer="bar")
    assert str(e.value) == "bad producer instance"

    with pytest.raises(AssertionError) as e:
        Queue(topic="topic", producer=producer, serializer="baz")
    assert str(e.value) == "serializer must be a callable"

    with pytest.raises(AssertionError) as e:
        Queue(topic="topic", producer=producer, timeout="bar")
    assert str(e.value) == "timeout must be an int or float"

    with pytest.raises(AssertionError) as e:
        Queue(topic="topic", producer=producer, timeout=-1)
    assert str(e.value) == "timeout must be 0 or greater"

    with pytest.raises(AssertionError) as e:
        Queue(topic="topic", producer=producer, logger=1)
    assert str(e.value) == "bad logger instance"


def test_queue_enqueue_function(queue, func, topic, log):
    job = queue.enqueue(func, 1, 2)
    assert isinstance(job, Job)
    assert job.id is not None
    assert job.timestamp is not None
    assert job.topic == topic
    assert job.func == func
    assert job.args == (1, 2)
    assert job.kwargs == {}
    assert job.timeout == 0
    assert job.key is None
    assert job.partition is None
    assert log.last_line == "[INFO] Enqueueing {} ...".format(job)


def test_queue_enqueue_function_with_spec(func, queue, topic, log):
    job = queue.using(key=b"foo", partition=0).enqueue(func, 3, 4)
    assert isinstance(job, Job)
    assert job.id is not None
    assert job.timestamp is not None
    assert job.topic == topic
    assert job.func == func
    assert job.args == (3, 4)
    assert job.kwargs == {}
    assert job.timeout == 0
    assert job.key == b"foo"
    assert job.partition == 0
    assert log.last_line == "[INFO] Enqueueing {} ...".format(job)


# noinspection PyTypeChecker
def test_queue_enqueue_function_with_bad_args(func, queue):
    with pytest.raises(AssertionError) as e:
        queue.enqueue(1)
    assert str(e.value) == "first argument must be a callable"

    with pytest.raises(AssertionError) as e:
        queue.using(timeout="foo").enqueue(func)
    assert str(e.value) == "timeout must be an int or float"

    with pytest.raises(AssertionError) as e:
        queue.using(key="foo").enqueue(func)
    assert str(e.value) == "key must be a bytes"

    with pytest.raises(AssertionError) as e:
        queue.using(partition="foo").enqueue(func)
    assert str(e.value) == "partition must be an int"


def test_queue_enqueue_job_fully_populated(func, queue, topic, log):
    job_id = uuid.uuid4().hex
    timestamp = int(time.time() * 1000)

    job = Job(
        id=job_id,
        timestamp=timestamp,
        topic="topic",
        func=func,
        args=[0],
        kwargs={"b": 1},
        timeout=10,
        key=b"bar",
        partition=0,
    )
    job = queue.enqueue(job)
    assert isinstance(job, Job)
    assert job.id == job_id
    assert job.timestamp >= timestamp
    assert job.topic == topic
    assert job.func == func
    assert job.args == (0,)
    assert job.kwargs == {"b": 1}
    assert job.timeout == 10
    assert job.key == b"bar"
    assert job.partition == 0
    assert log.last_line.startswith("[INFO] Enqueueing {} ...".format(job))


def test_queue_enqueue_job_partially_populated(func, queue, topic, log):
    job = Job(func=func, args=[1], kwargs={"b": 1})

    job = queue.enqueue(job)
    assert isinstance(job, Job)
    assert isinstance(job.id, str)
    assert isinstance(job.timestamp, int)
    assert job.topic == topic
    assert job.func == func
    assert job.args == (1,)
    assert job.kwargs == {"b": 1}
    assert job.timeout == 0
    assert job.key is None
    assert job.partition is None
    assert log.last_line.startswith("[INFO] Enqueueing {} ...".format(job))


def test_queue_enqueue_job_with_spec(func, queue, topic, log):
    job_id = uuid.uuid4().hex
    timestamp = int(time.time() * 1000)

    job = Job(
        id=job_id,
        timestamp=timestamp,
        topic="topic",
        func=func,
        args=[0],
        kwargs={"b": 1},
        timeout=10,
        key=b"bar",
        partition=0,
    )

    # Job should override the spec.
    job = queue.using(key=b"foo", timeout=5, partition=5).enqueue(job)
    assert isinstance(job, Job)
    assert job.id == job_id
    assert job.timestamp >= timestamp
    assert job.topic == topic
    assert job.func == func
    assert job.args == (0,)
    assert job.kwargs == {"b": 1}
    assert job.timeout == 10
    assert job.key == b"bar"
    assert job.partition == 0
    assert log.last_line.startswith("[INFO] Enqueueing {} ...".format(job))


def test_queue_enqueue_job_with_bad_args(func, queue, topic):
    valid_job_kwargs = {
        "id": uuid.uuid4().hex,
        "timestamp": int(time.time() * 1000),
        "topic": topic,
        "func": func,
        "args": [0],
        "kwargs": {"b": 1},
        "timeout": 10,
        "key": b"foo",
        "partition": 0,
    }

    def build_job(**kwargs):
        job_kwargs = valid_job_kwargs.copy()
        job_kwargs.update(kwargs)
        return Job(**job_kwargs)

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(id=1))
    assert str(e.value) == "Job.id must be a str"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(func=1))
    assert str(e.value) == "Job.func must be a callable"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(args=1))
    assert str(e.value) == "Job.args must be a list or tuple"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(kwargs=1))
    assert str(e.value) == "Job.kwargs must be a dict"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(timeout="foo"))
    assert str(e.value) == "Job.timeout must be an int or float"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(key="foo"))
    assert str(e.value) == "Job.key must be a bytes"

    with pytest.raises(AssertionError) as e:
        queue.enqueue(build_job(partition="foo"))
    assert str(e.value) == "Job.partition must be an int"
