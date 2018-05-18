Job
----

KQ encapsulates jobs using ``kq.Job`` namedtuples, which have the following
fields:

* **id** (str): Job ID.
* **timestamp** (int): Unix timestamp indicating the time of enqueue.
* **topic** (str): Name of the Kafka topic.
* **func** (callable): Function to execute.
* **args** (list | tuple): Positional arguments for the function.
* **kwargs** (dict): Keyword arguments for the function.
* **timeout** (int | float): Job timeout threshold in seconds.
* **key** (bytes | None): Kafka message key. Jobs with the same keys are sent
  to the same topic partition and executed sequentially. Applies only if the
  **partition** field is not set, and the producer's partitioner configuration
  is left as default.
* **partition** (int | None): Kafka topic partition. If set, the **key** field
  is ignored.

.. testcode::

    from collections import namedtuple

    Job = namedtuple(
        typename='Job',
        field_names=(
            'id',
            'timestamp',
            'topic',
            'func',
            'args',
            'kwargs',
            'timeout',
            'key',
            'partition'
        )
    )

When a function call is enqueued, an instance of this namedtuple is created to
store the metadata. It is then serialized into a byte string and sent to Kafka.
