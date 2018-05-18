Message
-------

KQ encapsulates Kafka messages using ``kq.Message`` namedtuples, which have
the following fields:

* **topic** (str): Name of the Kafka topic.
* **partition** (int): Kafka topic partition.
* **offset** (int): Partition offset.
* **key** (bytes | None): Kafka message key.
* **value** (bytes): Kafka message payload.

.. testcode::

    from collections import namedtuple

    Message = namedtuple(
        typename='Message',
        field_names=(
            'topic',
            'partition',
            'offset',
            'key',
            'value'
        )
    )

Raw Kafka messages are converted into these namedtuples, which are then sent
to :doc:`workers <worker>` (and also to :doc:`callback functions <callback>`
if defined).
