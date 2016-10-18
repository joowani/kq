from __future__ import absolute_import, print_function, unicode_literals


def rec_repr(record):
    """Return the string representation of the consumer record.

    :param record: Record fetched from the Kafka topic.
    :type record: kafka.consumer.fetcher.ConsumerRecord
    :return: String representation of the consumer record.
    :rtype: str | unicode
    """
    return 'Record(topic={}, partition={}, offset={})'.format(
        record.topic, record.partition, record.offset
    )


def func_repr(func, args, kwargs):
    """Return the string representation of the function call.

    :param func: Function to represent.
    :type func: callable
    :param args: Function arguments.
    :type args: list | collections.Iterable
    :param kwargs: Function keyword arguments.
    :type kwargs: dict | collections.Mapping
    :return: String representation of the function call.
    :rtype: str | unicode
    """
    params = list(map(repr, args))
    params.extend(k + '=' + repr(v) for k, v in sorted(kwargs.items()))
    return '{}.{}({})'.format(
        getattr(func, '__module__', '?'),
        getattr(func, '__name__', '?'),
        ', '.join(params)
    )
