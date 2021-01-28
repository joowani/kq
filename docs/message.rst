Message
-------

KQ encapsulates Kafka messages using ``kq.Message`` dataclass:

.. testcode::

    from dataclasses import dataclass
    from typing import Optional


    @dataclass(frozen=True)
    class Message:
        # Name of the Kafka topic.
        topic: str

        # Kafka topic partition.
        partition: int

        # Partition offset.
        offset: int

        # Kafka message key.
        key: Optional[bytes]

        # Kafka message payload.
        value: bytes

Raw Kafka messages are converted into above dataclasses, which are then sent
to :doc:`workers <worker>` (and also to :doc:`callback functions <callback>`
if defined).
