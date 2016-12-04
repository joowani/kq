from __future__ import absolute_import, print_function, unicode_literals

import kafka


# TODO need to add more functionality
class Manager(object):
    """KQ manager.

    Here is an example of initializing and using a manager:

    .. code-block:: python

        from kq import Manager

        manager = Manager(
            hosts='host:7000,host:8000',
            cafile='/my/files/cafile',
            certfile='/my/files/certfile',
            keyfile='/my/files/keyfile',
            crlfile='/my/files/crlfile'
        )
        manager.info()

    .. note::

        There is not much happening with this class right now. It's still
        a work in progress.

    :param hosts: Comma-separated Kafka hostnames and ports. For example,
        ``"localhost:9000,localhost:8000,192.168.1.1:7000"`` is a valid
        input string. Default: ``"127.0.0.1:9092"``.
    :type hosts: str | unicode
    :param cafile: Full path to the trusted CA certificate file.
    :type cafile: str | unicode
    :param certfile: Full path to the client certificate file.
    :type certfile: str | unicode
    :param keyfile: Full path to the client private key file.
    :type keyfile: str | unicode
    :param crlfile: Full path to the CRL file for validating certification
        expiry. This option is only available with Python 3.4+ or 2.7.9+.
    :type crlfile: str | unicode
    """

    def __init__(self,
                 hosts='127.0.0.1:9092',
                 cafile=None,
                 certfile=None,
                 keyfile=None,
                 crlfile=None):
        self._hosts = hosts
        self._consumer = kafka.KafkaConsumer(
            bootstrap_servers=self._hosts,
            ssl_cafile=cafile,
            ssl_certfile=certfile,
            ssl_keyfile=keyfile,
            ssl_crlfile=crlfile,
            consumer_timeout_ms=-1,
            enable_auto_commit=True,
            auto_offset_reset='latest',
        )

    def __repr__(self):
        """Return a string representation of the queue.

        :return: string representation of the queue
        :rtype: str | unicode
        """
        return 'Manager(hosts={})'.format(self._hosts)

    @property
    def consumer(self):
        """Return the Kafka consumer object.

        :return: Kafka consumer object.
        :rtype: kafka.consumer.KafkaConsumer
        """
        return self._consumer

    @property
    def hosts(self):
        """Return the list of Kafka host names and ports.

        :return: list of Kafka host names and ports
        :rtype: [str]
        """
        return self._hosts.split(',')

    def info(self):
        """Print the offset information for all topics and partitions."""
        print('Offsets per Topic:')
        for topic in self._consumer.topics():
            print('\nTopic {}:\n'.format(topic))
            partitions = self._consumer.partitions_for_topic(topic)
            if partitions is None:  # pragma: no cover
                print('    Polling failed (please try again)')
                continue
            for partition in self._consumer.partitions_for_topic(topic):
                topic_partition = kafka.TopicPartition(topic, partition)
                self._consumer.assign([topic_partition])
                offset = self._consumer.position(topic_partition)
                print('    Partition {:<3}: {}'.format(partition, offset))
