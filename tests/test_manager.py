from __future__ import absolute_import, print_function, unicode_literals

import mock
import pytest

from kq import Manager

from .utils import CaptureOutput

expected_info_output = """
Offsets per Topic:

Topic foo:

    Partition 1  : 100
    Partition 2  : 100
    Partition 3  : 100

Topic bar:

    Partition 1  : 100
    Partition 2  : 100
    Partition 3  : 100

Topic baz:

    Partition 1  : 100
    Partition 2  : 100
    Partition 3  : 100
"""


@pytest.fixture(autouse=True)
def consumer(monkeypatch):
    mock_consumer_inst = mock.MagicMock()
    mock_consumer_inst.topics.return_value = ['foo', 'bar', 'baz']
    mock_consumer_inst.partitions_for_topic.return_value = [1, 2, 3]
    mock_consumer_inst.position.return_value = 100
    mock_consumer_cls = mock.MagicMock()
    mock_consumer_cls.return_value = mock_consumer_inst
    monkeypatch.setattr('kafka.KafkaConsumer', mock_consumer_cls)
    return mock_consumer_cls, mock_consumer_inst


def test_init(consumer):
    consumer_cls, consumer_inst = consumer

    manager = Manager(
        hosts='host:7000,host:8000',
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    consumer_cls.assert_called_with(
        bootstrap_servers='host:7000,host:8000',
        ssl_cafile='/test/files/cafile',
        ssl_certfile='/test/files/certfile',
        ssl_keyfile='/test/files/keyfile',
        ssl_crlfile='/test/files/crlfile',
        consumer_timeout_ms=-1,
        enable_auto_commit=True,
        auto_offset_reset='latest',
    )
    assert repr(manager) == 'Manager(hosts=host:7000,host:8000)'
    assert manager.hosts == ['host:7000', 'host:8000']
    assert manager.consumer == consumer_inst


def test_info():
    manager = Manager(
        hosts='host:7000,host:8000',
        cafile='/test/files/cafile',
        certfile='/test/files/certfile',
        keyfile='/test/files/keyfile',
        crlfile='/test/files/crlfile'
    )
    with CaptureOutput() as output:
        manager.info()
    assert len(output) == 1
    assert '\n' + output[0] == expected_info_output
