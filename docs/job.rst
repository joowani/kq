Job
----

KQ encapsulates jobs using namedtuples_. The definition is as follows:

.. code-block:: python

    from collections import namedtuple

    Job = namedtuple(
        typename='Job',
        field_names=[
            'id',         # UUID of the job
            'timestamp',  # Unix timestamp indicating when the job was queued
            'topic',      # Name of the Kafka topic the job was enqueued in
            'func',       # Job function/callable
            'args',       # Job function arguments
            'kwargs',     # Job function keyword arguments
            'timeout',    # Job timeout threshold in seconds
            'key'         # Jobs w/ the same keys end up in the same partition
        ]
    )

When a function call is enqueued, an instance of the job namedtuple is created.
The instance is then serialized using the dill_ Python library and placed in a
Kafka topic. A worker then fetches, de-serializes and executes the job.

.. _dill: https://github.com/uqfoundation/dill
.. _namedtuples:
    https://docs.python.org/2/library/collections.html#collections.namedtuple