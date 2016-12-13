from __future__ import absolute_import, print_function, unicode_literals

import time

import dill
import mock
import pytest

from kq import Job, Queue

from .utils import (
    success_func,
    failure_func
)


@pytest.fixture(autouse=True)
def producer(monkeypatch):
    mock_producer_inst = mock.MagicMock()
    mock_producer_cls = mock.MagicMock()
    mock_producer_cls.return_value = mock_producer_inst
    monkeypatch.setattr('kafka.KafkaProducer', mock_producer_cls)
    return mock_producer_cls, mock_producer_inst


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    mock_logger_inst = mock.MagicMock()
    mock_get_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger_inst
    monkeypatch.setattr('logging.getLogger', mock_get_logger)
    return mock_logger_inst


def test_init(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(
        hosts='host:7000,host:8000',
        topic='foo',
        timeout=1000,
        compression='gzip',
        acks=0,
        retries=5,
        job_size=10000000,
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    producer_cls.assert_called_with(
        bootstrap_servers='host:7000,host:8000',
        compression_type='gzip',
        acks=0,
        retries=5,
        max_request_size=10000000,
        buffer_memory=33554432,
        ssl_cafile='/test/files/cafile',
        ssl_certfile='/test/files/certfile',
        ssl_keyfile='/test/files/keyfile',
        ssl_crlfile='/test/files/crlfile',
    )
    assert repr(queue) == 'Queue(topic=foo)'
    assert queue.hosts == ['host:7000', 'host:8000']
    assert queue.timeout == 1000
    assert queue.topic == 'foo'
    assert queue.producer == producer_inst
    assert not logger.info.called


def test_enqueue_call(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)
    job = queue.enqueue(success_func, 1, 2, c=[3, 4, 5])

    assert isinstance(job, Job)
    assert isinstance(job.id, str)
    assert isinstance(job.timestamp, int)
    assert job.topic == 'foo'
    assert job.func == success_func
    assert job.args == (1, 2)
    assert job.kwargs == {'c': [3, 4, 5]}
    assert job.timeout == 300

    producer_inst.send.assert_called_with('foo', dill.dumps(job), key=None)
    logger.info.assert_called_once_with('Enqueued: {}'.format(job))


def test_enqueue_call_with_key(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)
    job = queue.enqueue_with_key('bar', success_func, 1, 2, c=[3, 4, 5])

    assert isinstance(job, Job)
    assert isinstance(job.id, str)
    assert isinstance(job.timestamp, int)
    assert job.topic == 'foo'
    assert job.func == success_func
    assert job.args == (1, 2)
    assert job.kwargs == {'c': [3, 4, 5]}
    assert job.timeout == 300
    assert job.key == 'bar'

    producer_inst.send.assert_called_with('foo', dill.dumps(job), key='bar')
    logger.info.assert_called_once_with('Enqueued: {}'.format(job))


def test_invalid_call(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)

    for bad_func in [None, 1, {1, 2}, [1, 2, 3]]:
        with pytest.raises(ValueError) as e:
            queue.enqueue(bad_func, 1, 2, a=3)
        assert str(e.value) == '{} is not a callable'.format(bad_func)

    assert not producer_inst.send.called
    assert not logger.info.called


def test_invalid_call_with_key(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)

    for bad_func in [None, 1, {1, 2}, [1, 2, 3]]:
        with pytest.raises(ValueError) as e:
            queue.enqueue_with_key('foo', bad_func, 1, 2, a=3)
        assert str(e.value) == '{} is not a callable'.format(bad_func)

    assert not producer_inst.send.called
    assert not logger.info.called


def test_enqueue_job(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)

    old_job = Job(
        id='2938401',
        timestamp=int(time.time()),
        topic='bar',
        func=failure_func,
        args=[1, 2],
        kwargs={'a': 3},
        timeout=100,
    )
    new_job = queue.enqueue(old_job)

    assert isinstance(new_job, Job)
    assert isinstance(new_job.id, str)
    assert isinstance(new_job.timestamp, int)
    assert old_job.id != new_job.id
    assert old_job.timestamp <= new_job.timestamp
    assert new_job.topic == 'foo'
    assert new_job.func == failure_func
    assert new_job.args == [1, 2]
    assert new_job.kwargs == {'a': 3}
    assert new_job.timeout == 300
    assert new_job.key == None

    producer_inst.send.assert_called_with(
        'foo', dill.dumps(new_job), key=None
    )
    logger.info.assert_called_once_with('Enqueued: {}'.format(new_job))


def test_enqueue_job_with_key(producer, logger):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo', timeout=300)

    old_job = Job(
        id='2938401',
        timestamp=int(time.time()),
        topic='bar',
        func=failure_func,
        args=[1, 2],
        kwargs={'a': 3},
        timeout=100,
        key='bar',
    )
    new_job = queue.enqueue_with_key('baz', old_job)

    assert isinstance(new_job, Job)
    assert isinstance(new_job.id, str)
    assert isinstance(new_job.timestamp, int)
    assert old_job.id != new_job.id
    assert old_job.timestamp <= new_job.timestamp
    assert new_job.topic == 'foo'
    assert new_job.func == failure_func
    assert new_job.args == [1, 2]
    assert new_job.kwargs == {'a': 3}
    assert new_job.timeout == 300
    assert new_job.key == 'baz'

    producer_inst.send.assert_called_with(
        'foo', dill.dumps(new_job), key='baz'
    )
    logger.info.assert_called_once_with('Enqueued: {}'.format(new_job))


def test_job_decorator():
    queue = Queue(hosts='host:7000', topic='foo')

    @queue.job
    def test_function(a, b, c=None):
        return a, b, c
    assert hasattr(test_function, 'delay')

    with pytest.raises(Exception) as e:
        test_function.delay(1, 2, 3, 4)
    assert "Can't pickle" in str(e.value)


def test_flush(producer):
    producer_cls, producer_inst = producer

    queue = Queue(hosts='host:7000', topic='foo')
    queue.flush()
    producer_inst.flush.assert_called_once()

