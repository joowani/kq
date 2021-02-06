Callback
--------

KQ lets you assign a callback function to workers. The callback function is invoked
each time a message is processed. It must accept the following positional arguments:

* **status** (str): Job status. Possible values are:

    * ``invalid`` : Job could not be deserialized, or was malformed.
    * ``failure`` : Job raised an exception.
    * ``timeout`` : Job took too long and timed out.
    * ``success`` : Job successfully finished and returned a result.

* **message** (:doc:`kq.Message <message>`): Kafka message.
* **job** (:doc:`kq.Job <job>` | None): Job object, or None if Kafka message
  was invalid or malformed.
* **result** (object | None): Job result, or None if an exception was raised.
* **exception** (Exception | None): Exception raised, or None if job finished
  successfully.
* **stacktrace** (str | None): Exception stacktrace, or None if job finished
  successfully.

You can assign your callback function during :doc:`worker <worker>` initialization.

**Example:**

.. testcode::

    from kafka import KafkaConsumer
    from kq import Worker


    def callback(status, message, job, result, exception, stacktrace):
        """This is an example callback showing what arguments to expect."""

        assert status in ['invalid', 'success', 'timeout', 'failure']
        assert isinstance(message, kq.Message)

        if status == 'invalid':
            assert job is None
            assert result is None
            assert exception is None
            assert stacktrace is None

        if status == 'success':
            assert isinstance(job, kq.Job)
            assert exception is None
            assert stacktrace is None

        elif status == 'timeout':
            assert isinstance(job, kq.Job)
            assert result is None
            assert exception is None
            assert stacktrace is None

        elif status == 'failure':
            assert isinstance(job, kq.Job)
            assert result is None
            assert exception is not None
            assert stacktrace is not None

    consumer = KafkaConsumer(
        bootstrap_servers='127.0.0.1:9092',
        group_id='group'
    )

    # Inject your callback function during worker initialization.
    worker = Worker('topic', consumer, callback=callback)
