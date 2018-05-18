__all__ = ['Message']

from collections import namedtuple

# Namedtuple which encapsulates a Kafka message.
Message = namedtuple(
    typename='Message',
    field_names=(
        'topic',      # Name of the Kafka topic (str)
        'partition',  # Topic partition (int)
        'offset',     # Offset (int)
        'key',        # Message key (bytes | None)
        'value'       # Message value (bytes)
    )
)
