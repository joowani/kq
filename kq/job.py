__all__ = ['Job']

from collections import namedtuple

# Namedtuple which encapsulates a KQ job.
Job = namedtuple(
    typename='Job',
    field_names=(
        'id',         # Job ID (str)
        'timestamp',  # Unix timestamp indicating when job was enqueued (int)
        'topic',      # Name of the Kafka topic (str)
        'func',       # Function to execute (callable)
        'args',       # Positional arguments (list)
        'kwargs',     # Keyword arguments (dict)
        'timeout',    # Job timeout threshold in seconds (int | float)
        'key',        # Kafka message key if any (str | None)
        'partition'   # Kafka topic partition if any (str | None)
    )
)

# noinspection PyUnresolvedReferences,PyProtectedMember
Job.__new__.__defaults__ = (None,) * len(Job._fields)
