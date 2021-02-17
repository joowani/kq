import logging
from inspect import isbuiltin, isclass, isfunction, ismethod
from typing import Any, Callable


# noinspection PyUnresolvedReferences
def get_call_repr(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """Return the string representation of the function call.

    :param func: A callable (e.g. function, method).
    :type func: callable
    :param args: Positional arguments for the callable.
    :param kwargs: Keyword arguments for the callable.
    :return: String representation of the function call.
    :rtype: str
    """
    # Functions, builtins and methods
    if ismethod(func) or isfunction(func) or isbuiltin(func):
        func_repr = f"{func.__module__}.{func.__qualname__}"
    # A callable class instance
    elif not isclass(func) and hasattr(func, "__call__"):
        func_repr = f"{func.__module__}.{func.__class__.__name__}"
    else:
        func_repr = repr(func)

    args_reprs = [repr(arg) for arg in args]
    kwargs_reprs = [k + "=" + repr(v) for k, v in sorted(kwargs.items())]
    return f'{func_repr}({", ".join(args_reprs + kwargs_reprs)})'


def is_none_or_logger(obj: Any) -> bool:
    return obj is None or isinstance(obj, logging.Logger)


def is_none_or_int(obj: Any) -> bool:
    return obj is None or isinstance(obj, int)


def is_none_or_bytes(obj: Any) -> bool:
    return obj is None or isinstance(obj, bytes)


def is_none_or_func(obj: Any) -> bool:
    return obj is None or callable(obj)


def is_str(obj: Any) -> bool:
    return isinstance(obj, str)


def is_number(obj: Any) -> bool:
    return isinstance(obj, (int, float))


def is_dict(obj: Any) -> bool:
    return isinstance(obj, dict)


def is_seq(obj: Any) -> bool:
    return isinstance(obj, (list, tuple))
