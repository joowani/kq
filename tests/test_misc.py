from __future__ import absolute_import, print_function, unicode_literals

from kq.job import Job
from kq.utils import func_repr
from kq.version import VERSION


def test_version():
    assert isinstance(VERSION, str)
    assert all(n.isdigit() for n in VERSION.split('.'))


def test_job():
    job = Job(1, 2, 3, 4, 5, 6, 7, 8)

    assert job.id == 1
    assert job.timestamp == 2
    assert job.topic == 3
    assert job.func == 4
    assert job.args == 5
    assert job.kwargs == 6
    assert job.timeout == 7
    assert job.key == 8


def test_func_repr():

    def f(a, b):
        return a + b

    expected = 'tests.test_misc.f()'
    assert func_repr(f, [], {}) == expected

    expected = 'tests.test_misc.f(1)'
    assert func_repr(f, [1], {}) == expected

    expected = 'tests.test_misc.f(1, 2)'
    assert func_repr(f, [1, 2], {}) == expected

    expected = 'tests.test_misc.f(a=1)'
    assert func_repr(f, [], {'a': 1}) == expected

    expected = 'tests.test_misc.f(a=1, b=2)'
    assert func_repr(f, [], {'a': 1, 'b': 2}) == expected

    expected = 'tests.test_misc.f(1, a=1)'
    assert func_repr(f, [1], {'a': 1}) == expected

    expected = 'tests.test_misc.f(1, 2, a=1)'
    assert func_repr(f, [1, 2], {'a': 1}) == expected

    expected = 'tests.test_misc.f(1, 2, a=1, b=2)'
    assert func_repr(f, [1, 2], {'a': 1, 'b': 2}) == expected
