from __future__ import absolute_import, print_function, unicode_literals

from collections import namedtuple

import dill
import mock
import pytest

from kq import Job, Worker

from .utils import (
    success_func,
    failure_func,
    timeout_func
)

MockRecord = namedtuple(
    'MockRecord',
    ['topic', 'partition', 'offset', 'value']
)
# Mocks for patching KafkaConsumer
mock_consumer = mock.MagicMock()
mock_consumer.topics.return_value = ['foo', 'bar', 'baz']
mock_consumer.partitions_for_topic.return_value = [1, 2, 3]
mock_consumer.position.return_value = 100
mock_consumer_cls = mock.MagicMock()
mock_consumer_cls.return_value = mock_consumer

# Mocks for patching the logging module
success_job = Job(
    id='100',
    timestamp=1,
    topic='foo',
    func=success_func,
    args=[1, 2],
    kwargs={'c': 3},
    timeout=None,
)
failure_job = Job(
    id='200',
    timestamp=2,
    topic='foo',
    func=failure_func,
    args=[1, 2, 3],
    kwargs={},
    timeout=100,
)
timeout_job = Job(
    id='300',
    timestamp=3,
    topic='foo',
    func=timeout_func,
    args=[2, 3, 4],
    kwargs={},
    timeout=100,
)
value1 = dill.dumps(success_job)
value2 = dill.dumps(failure_job)
value3 = dill.dumps(timeout_job)
value4 = 'This is an unpicklable value'
value5 = dill.dumps(['This is not a job!'])

# Mocks for consumer records
rec11 = MockRecord(topic='foo', partition=1, offset=1, value=value1)
rec11_repr = 'Record(topic=foo, partition=1, offset=1)'
rec12 = MockRecord(topic='foo', partition=1, offset=2, value=value2)
rec12_repr = 'Record(topic=foo, partition=1, offset=2)'
rec21 = MockRecord(topic='foo', partition=2, offset=1, value=value3)
rec21_repr = 'Record(topic=foo, partition=2, offset=1)'
rec22 = MockRecord(topic='foo', partition=2, offset=2, value=value4)
rec22_repr = 'Record(topic=foo, partition=2, offset=2)'
rec34 = MockRecord(topic='foo', partition=3, offset=4, value=value5)
rec34_repr = 'Record(topic=foo, partition=3, offset=4)'


@pytest.fixture(autouse=True)
def consumer(monkeypatch):
    monkeypatch.setattr('kafka.KafkaConsumer', mock_consumer_cls)
    mock_consumer.reset_mock()


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    mock_logger = mock.MagicMock()
    mock_get_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger
    monkeypatch.setattr('logging.getLogger', mock_get_logger)
    return mock_logger


@pytest.fixture(autouse=True)
def callback():
    return mock.MagicMock()


def test_init(logger, callback):
    worker = Worker(
        hosts='host:7000,host:8000',
        topic='foo',
        timeout=1000,
        callback=callback,
        job_size=10000000,
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    mock_consumer_cls.assert_called_once_with(
        'foo',
        group_id='foo',
        bootstrap_servers='host:7000,host:8000',
        max_partition_fetch_bytes=20000000,
        ssl_cafile='/test/files/cafile',
        ssl_certfile='/test/files/certfile',
        ssl_keyfile='/test/files/keyfile',
        ssl_crlfile='/test/files/crlfile',
        consumer_timeout_ms=-1,
        enable_auto_commit=False,
        auto_offset_reset='latest',
    )
    assert repr(worker) == 'Worker(topic=foo)'
    assert worker.hosts == ['host:7000', 'host:8000']
    assert worker.timeout == 1000
    assert worker.topic == 'foo'
    assert worker.consumer == mock_consumer
    assert not callback.called
    assert not logger.info.called


def test_start_job_success(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec11])
    worker = Worker(
        hosts='localhost',
        topic='foo',
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec11_repr)),
        mock.call('Running Job 100: tests.utils.success_func(1, 2, c=3) ...'),
        mock.call('Job 100 returned: (1, 2, 3)'),
        mock.call('Executing callback ...')
    ])
    callback.assert_called_once_with(
        'success', success_job, (1, 2, 3), None, None
    )


def test_start_job_failure(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec12])
    worker = Worker(
        hosts='localhost',
        topic='foo',
        timeout=1000,
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec12_repr)),
        mock.call('Running Job 200: tests.utils.failure_func(1, 2, 3) ...'),
        mock.call('Executing callback ...')
    ])
    logger.exception.assert_called_with('Job 200 failed: failed!')
    assert len(callback.call_args_list) == 1

    callback_args = callback.call_args_list[0][0]
    assert callback_args[0] == 'failure'
    assert callback_args[1] == failure_job
    assert callback_args[2] is None
    assert isinstance(callback_args[3], ValueError)
    assert isinstance(callback_args[4], str)


def test_start_job_timeout(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec21])
    worker = Worker(
        hosts='localhost',
        topic='foo',
        timeout=1000,
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec21_repr)),
        mock.call('Running Job 300: tests.utils.timeout_func(2, 3, 4) ...'),
        mock.call('Executing callback ...')
    ])
    logger.error.assert_called_once_with(
        'Job 300 timed out after 100 seconds.'
    )
    callback.assert_called_once_with(
        'timeout', timeout_job, None, None, None
    )


def test_start_job_unloadable(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec22])
    worker = Worker(
        hosts='localhost',
        topic='foo',
        timeout=1000,
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec22_repr)),
    ])
    logger.warning.assert_called_once_with(
        '{} unloadable. Skipping ...'.format(rec22_repr)
    )
    assert not callback.called


def test_start_job_malformed(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec34])
    worker = Worker(
        hosts='localhost',
        topic='foo',
        timeout=1000,
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec34_repr)),
    ])
    logger.warning.assert_called_once_with(
        '{} malformed. Skipping ...'.format(rec34_repr)
    )
    assert not callback.called


def test_start_job_callback_fail(logger, callback):
    mock_consumer.__iter__ = lambda x: iter([rec11])
    expected_error = KeyError('foo')
    callback.side_effect = expected_error
    worker = Worker(
        hosts='localhost',
        topic='foo',
        callback=callback,
    )
    worker.start()
    logger.info.assert_has_calls([
        mock.call('Starting Worker(topic=foo) ...'),
        mock.call('Processing {} ...'.format(rec11_repr)),
        mock.call('Running Job 100: tests.utils.success_func(1, 2, c=3) ...'),
        mock.call('Job 100 returned: (1, 2, 3)'),
        mock.call('Executing callback ...')
    ])
    logger.exception.assert_called_once_with(
        'Callback failed: {}'.format(expected_error)
    )
