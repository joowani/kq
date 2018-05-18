from kq import Message


def test_message_init_with_args():
    job = Message(1, 2, 3, 4, 5)
    assert job.topic == 1
    assert job.partition == 2
    assert job.offset == 3
    assert job.key == 4
    assert job.value == 5


def test_message_init_with_kwargs():
    job = Message(
        topic=1,
        partition=2,
        offset=3,
        key=4,
        value=5,
    )
    assert job.topic == 1
    assert job.partition == 2
    assert job.offset == 3
    assert job.key == 4
    assert job.value == 5
