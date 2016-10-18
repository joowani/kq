from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys

import mock
import pytest

from kq import cli, VERSION

from .utils import CaptureOutput

patch_object = getattr(mock.patch, 'object')


@pytest.fixture(autouse=True)
def manager(monkeypatch):
    mock_manager_inst = mock.MagicMock()
    mock_manager_cls = mock.MagicMock(return_value=mock_manager_inst)
    monkeypatch.setattr('kq.Manager', mock_manager_cls)
    return mock_manager_cls, mock_manager_inst


@pytest.fixture(autouse=True)
def worker(monkeypatch):
    mock_worker_inst = mock.MagicMock()
    mock_worker_cls = mock.MagicMock(return_value=mock_worker_inst)
    monkeypatch.setattr('kq.Worker', mock_worker_cls)
    return mock_worker_cls, mock_worker_inst


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    mock_logger_inst = mock.MagicMock()
    mock_get_logger = mock.MagicMock()
    mock_get_logger.return_value = mock_logger_inst
    monkeypatch.setattr('logging.getLogger', mock_get_logger)
    return mock_logger_inst


def test_help_menu():
    with patch_object(sys, 'argv', ['kq', '--help']):
        with CaptureOutput() as output, pytest.raises(SystemExit):
            cli.entry_point()
        assert len(output) == 1
        assert 'Usage' in output[0]
        assert 'Options' in output[0]


def test_version():
    with patch_object(sys, 'argv', ['kq', '--version']):
        with CaptureOutput() as output, pytest.raises(SystemExit):
            cli.entry_point()
        assert len(output) == 1
        assert output[0] == VERSION + '\n'


def test_info(manager, logger):
    manager_cls, manager_inst = manager

    test_arguments = [
        'kq',
        'info',
        '--hosts=host:6000,host:7000',
        '--cafile=/test/files/cafile',
        '--certfile=/test/files/certfile',
        '--keyfile=/test/files/keyfile',
        '--crlfile=/test/files/crlfile'
    ]
    with patch_object(sys, 'argv', test_arguments):
        cli.entry_point()

    logger.setLevel.assert_called_once_with(logging.WARNING)
    manager_cls.assert_called_once_with(
        hosts='host:6000,host:7000',
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    manager_inst.info.assert_called_once()


def test_worker(worker, logger):
    worker_cls, worker_inst = worker

    test_arguments = [
        'kq',
        'worker',
        '--hosts=host:6000,host:7000',
        '--topic=foo',
        '--timeout=4000',
        '--job-size=3000000',
        '--cafile=/test/files/cafile',
        '--certfile=/test/files/certfile',
        '--keyfile=/test/files/keyfile',
        '--crlfile=/test/files/crlfile'
    ]
    with patch_object(sys, 'argv', test_arguments):
        cli.entry_point()

    logger.setLevel.assert_called_once_with(logging.WARNING)
    worker_cls.assert_called_once_with(
        hosts='host:6000,host:7000',
        topic='foo',
        timeout=4000,
        callback=None,
        job_size=3000000,
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    worker_inst.start.assert_called_once()


def test_callback(worker, logger):
    worker_cls, worker_inst = worker

    test_arguments = [
        'kq',
        'worker',
        '--hosts=host:6000,host:7000',
        '--topic=foo',
        '--timeout=4000',
        '--callback=/invalid/path'
    ]
    with patch_object(sys, 'argv', test_arguments):
        cli.entry_point()

    logger.exception.assert_called_once()
    logger.setLevel.assert_called_once_with(logging.WARNING)
    worker_cls.assert_called_with(
        hosts='host:6000,host:7000',
        topic='foo',
        timeout=4000,
        callback=None,
        job_size=1048576,
        cafile=None,
        certfile=None,
        keyfile=None,
        crlfile=None
    )
    worker_inst.start.assert_called_once()


def test_verbose(worker, logger):
    worker_cls, worker_inst = worker

    with patch_object(sys, 'argv', ['kq', 'worker', '--verbose']):
        cli.entry_point()

    logger.setLevel.assert_called_once_with(logging.DEBUG)
    worker_cls.assert_called_with(
        hosts='127.0.0.1',
        topic='default',
        timeout=None,
        callback=None,
        job_size=1048576,
        cafile=None,
        certfile=None,
        keyfile=None,
        crlfile=None
    )
    worker_inst.start.assert_called_once()
