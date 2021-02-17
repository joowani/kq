import pytest
from kafka import KafkaConsumer

from kq import Worker


def test_worker_properties(worker, hosts, topic, group):
    assert hosts in repr(worker)
    assert topic in repr(worker)
    assert group in repr(worker)

    assert worker.consumer.config["bootstrap_servers"] == hosts
    assert worker.consumer.config["group_id"] == group

    assert isinstance(worker.hosts, str) and worker.hosts == hosts
    assert isinstance(worker.topic, str) and worker.topic == topic
    assert isinstance(worker.group, str) and worker.group == group
    assert isinstance(worker.consumer, KafkaConsumer)
    assert callable(worker.deserializer)
    assert callable(worker.callback) or worker.callback is None


# noinspection PyTypeChecker
def test_worker_initialization_with_bad_args(hosts, consumer):
    with pytest.raises(AssertionError) as e:
        Worker(topic=True, consumer=consumer)
    assert str(e.value) == "topic must be a str"

    with pytest.raises(AssertionError) as e:
        Worker(topic="topic", consumer="bar")
    assert str(e.value) == "bad consumer instance"

    with pytest.raises(AssertionError) as e:
        bad_consumer = KafkaConsumer(bootstrap_servers=hosts)
        Worker(topic="topic", consumer=bad_consumer)
    assert str(e.value) == "consumer must have group_id"

    with pytest.raises(AssertionError) as e:
        Worker(topic="topic", consumer=consumer, callback=1)
    assert str(e.value) == "callback must be a callable"

    with pytest.raises(AssertionError) as e:
        Worker(topic="topic", consumer=consumer, deserializer=1)
    assert str(e.value) == "deserializer must be a callable"

    with pytest.raises(AssertionError) as e:
        Worker(topic="topic", consumer=consumer, logger=1)
    assert str(e.value) == "bad logger instance"


def test_worker_run_success_function(queue, worker, success_func, log):
    job = queue.enqueue(success_func, 1, 2)
    worker.start(max_messages=1)

    out = log.last_lines(7)
    assert next(out).startswith(f"[INFO] Enqueueing {job}")
    assert next(out).startswith(f"[INFO] Starting {worker}")
    assert next(out).startswith("[INFO] Processing Message")
    assert next(out).startswith(f"[INFO] Executing job {job.id}")
    assert next(out).startswith(f"[INFO] Job {job.id} returned: 2")
    assert next(out).startswith("[INFO] Executing callback")
    assert next(out).startswith('[INFO] Callback got job status "success"')


def test_worker_run_failure_function(queue, worker, failure_func, log):
    job = queue.enqueue(failure_func, 2, 3)
    worker.start(max_messages=1)

    out = log.last_lines(7)
    assert next(out).startswith(f"[INFO] Enqueueing {job}")
    assert next(out).startswith(f"[INFO] Starting {worker}")
    assert next(out).startswith("[INFO] Processing Message")
    assert next(out).startswith(f"[INFO] Executing job {job.id}")
    assert next(out).startswith(f"[ERROR] Job {job.id} raised")
    assert next(out).startswith("[INFO] Executing callback")
    assert next(out).startswith('[INFO] Callback got job status "failure"')


def test_worker_run_timeout_function(queue, worker, timeout_func, log):
    job = queue.using(timeout=0.5).enqueue(timeout_func, 3, 4)
    worker.start(max_messages=1)

    out = log.last_lines(7)
    assert next(out).startswith(f"[INFO] Enqueueing {job}")
    assert next(out).startswith(f"[INFO] Starting {worker}")
    assert next(out).startswith("[INFO] Processing Message")
    assert next(out).startswith(f"[INFO] Executing job {job.id}")
    assert next(out).startswith(f"[ERROR] Job {job.id} timed out")
    assert next(out).startswith("[INFO] Executing callback")
    assert next(out).startswith('[INFO] Callback got job status "timeout"')


def test_worker_run_bad_callback(queue, worker, success_func, callback, log):
    job = queue.enqueue(success_func, 4, 5)
    callback.succeed = False
    worker.start(max_messages=1)

    out = log.last_lines(7)
    assert next(out).startswith(f"[INFO] Enqueueing {job}")
    assert next(out).startswith(f"[INFO] Starting {worker}")
    assert next(out).startswith("[INFO] Processing Message")
    assert next(out).startswith(f"[INFO] Executing job {job.id}")
    assert next(out).startswith(f"[INFO] Job {job.id} returned: 20")
    assert next(out).startswith("[INFO] Executing callback")
    assert next(out).startswith("[ERROR] Callback raised an exception")


def test_worker_run_bad_job(queue, worker, success_func, deserializer, log):
    job = queue.enqueue(success_func, 5, 6)
    deserializer.succeed = False
    worker.start(max_messages=1)

    out = log.last_lines(6)
    assert next(out).startswith(f"[INFO] Enqueueing {job}")
    assert next(out).startswith(f"[INFO] Starting {worker}")
    assert next(out).startswith("[INFO] Processing Message")
    assert next(out).startswith("[ERROR] Job was invalid")
    assert next(out).startswith("[INFO] Executing callback")
    assert next(out).startswith('[INFO] Callback got job status "invalid"')
