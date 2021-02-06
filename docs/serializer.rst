Serializer
----------

You can use custom functions for serialization. By default, KQ uses the dill_ library.

.. _dill: https://github.com/uqfoundation/dill

The serializer function must take a :doc:`job <job>` namedtuple and return a
byte string. You can inject it during queue initialization.

**Example:**

.. testcode::

    # Let's use pickle instead of dill
    import pickle

    from kafka import KafkaProducer
    from kq import Queue

    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

    # Inject your serializer function during queue initialization.
    queue = Queue('topic', producer, serializer=pickle.dumps)

The deserializer function must take a byte string and returns a :doc:`job <job>`
namedtuple. You can inject it during worker initialization.

**Example:**

.. testcode::

    # Let's use pickle instead of dill
    import pickle

    from kafka import KafkaConsumer
    from kq import Worker

    consumer = KafkaConsumer(
        bootstrap_servers='127.0.0.1:9092',
        group_id='group'
    )

    # Inject your deserializer function during worker initialization.
    worker = Worker('topic', consumer, deserializer=pickle.loads)
