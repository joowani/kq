from __future__ import absolute_import, print_function, unicode_literals

from collections import namedtuple


# Named tuple which encapsulates a KQ job
Job = namedtuple(
    typename='Job',
    field_names=[
        'id',         # UUID of the job
        'timestamp',  # Unix timestamp indicating when the job was queued
        'topic',      # Name of the Kafka topic the job was enqueued in
        'func',       # Job function/callable
        'args',       # Job function arguments
        'kwargs',     # Job function keyword arguments
        'timeout'     # Job timeout threshold in seconds
    ]
)
