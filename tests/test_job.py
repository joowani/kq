from kq import Job


def test_job_init_with_args():
    job = Job(1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert job.id == 1
    assert job.timestamp == 2
    assert job.topic == 3
    assert job.func == 4
    assert job.args == 5
    assert job.kwargs == 6
    assert job.timeout == 7
    assert job.key == 8
    assert job.partition == 9


def test_job_init_with_kwargs():
    job = Job(
        id=1,
        timestamp=2,
        topic=3,
        func=4,
        args=5,
        kwargs=6,
        timeout=7,
        key=8,
        partition=9
    )
    assert job.id == 1
    assert job.timestamp == 2
    assert job.topic == 3
    assert job.func == 4
    assert job.args == 5
    assert job.kwargs == 6
    assert job.timeout == 7
    assert job.key == 8
    assert job.partition == 9
