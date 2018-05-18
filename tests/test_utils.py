from kq.utils import get_call_repr


def test_call_repr_callable_types(success_func, callable_cls):
    expected = 'None()'
    assert expected == get_call_repr(None)

    expected = 'builtins.isinstance()'
    assert expected == get_call_repr(isinstance)

    expected = 'tests.conftest.success_function()'
    assert expected == get_call_repr(success_func)

    expected = 'tests.conftest.success_function()'
    assert expected == get_call_repr(callable_cls.unbound_method)

    expected = 'tests.conftest.Callable.static_method()'
    assert expected == get_call_repr(callable_cls.static_method)

    expected = 'tests.conftest.Callable.instance_method()'
    assert expected == get_call_repr(callable_cls().instance_method)

    expected = 'tests.conftest.Callable()'
    assert expected == get_call_repr(callable_cls())


def test_call_repr_simple_args(failure_func):
    expected = 'tests.conftest.failure_function(1)'
    assert expected == get_call_repr(failure_func, 1)

    expected = 'tests.conftest.failure_function(1, 2)'
    assert expected == get_call_repr(failure_func, 1, 2)

    expected = 'tests.conftest.failure_function(1, b=2)'
    assert expected == get_call_repr(failure_func, 1, b=2)

    expected = 'tests.conftest.failure_function(a=1)'
    assert expected == get_call_repr(failure_func, a=1)

    expected = 'tests.conftest.failure_function(b=1)'
    assert expected == get_call_repr(failure_func, b=1)

    expected = 'tests.conftest.failure_function(a=1, b=2)'
    assert expected == get_call_repr(failure_func, a=1, b=2)

    expected = 'tests.conftest.failure_function(a=1, b=2)'
    assert expected == get_call_repr(failure_func, b=2, a=1)


def test_call_repr_complex_args(timeout_func):
    expected = 'tests.conftest.timeout_function([1])'
    assert expected == get_call_repr(timeout_func, [1])

    expected = 'tests.conftest.timeout_function([1], [2])'
    assert expected == get_call_repr(timeout_func, [1], [2])

    expected = 'tests.conftest.timeout_function([1], b=[2])'
    assert expected == get_call_repr(timeout_func, [1], b=[2])

    expected = 'tests.conftest.timeout_function(a=[1])'
    assert expected == get_call_repr(timeout_func, a=[1])

    expected = 'tests.conftest.timeout_function(b=[1])'
    assert expected == get_call_repr(timeout_func, b=[1])

    expected = 'tests.conftest.timeout_function(a=[1], b=[1, 2])'
    assert expected == get_call_repr(timeout_func, a=[1], b=[1, 2])

    expected = 'tests.conftest.timeout_function(a=[1], b=[1, 2])'
    assert expected == get_call_repr(timeout_func, b=[1, 2], a=[1])
