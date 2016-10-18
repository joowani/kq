from __future__ import absolute_import, print_function, unicode_literals

import multiprocessing
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys


class CaptureOutput(list):

    def __enter__(self):
        self._orig_stdout = sys.stdout
        self._temp_stdout = StringIO()
        sys.stdout = self._temp_stdout
        return self

    def __exit__(self, *args):
        self.append(self._temp_stdout.getvalue())
        sys.stdout = self._orig_stdout


def success_func(a, b, c=None):
    return a, b, c


def failure_func(*_):
    raise ValueError('failed!')


def timeout_func(*_):
    raise multiprocessing.TimeoutError
