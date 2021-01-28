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
