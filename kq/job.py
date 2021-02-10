from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Union


@dataclass(frozen=True)
class Job:

    # KQ job UUID
    id: Optional[str] = None

    # Unix timestamp indicating when the job was queued.
    timestamp: Optional[int] = None

    # Name of the Kafka topic.
    topic: Optional[str] = None

    # Function to execute.
    func: Optional[Callable[..., Any]] = None

    # Positional arguments for the function.
    args: Optional[Sequence[Any]] = None

    # Keyword arguments for the function.
    kwargs: Optional[Dict[str, Any]] = None

    # Job timeout threshold in seconds.
    timeout: Optional[Union[float, int]] = None

    # Kafka message key. Jobs with the same keys are sent
    # to the same topic partition and executed sequentially.
    # Applies only when the "partition" field is not set.
    key: Optional[bytes] = None

    # Kafka topic partition. If set, the "key" field is ignored.
    partition: Optional[Union[float, int]] = None
