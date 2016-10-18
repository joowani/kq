from __future__ import absolute_import, print_function, unicode_literals

import logging

from kq.job import Job
from kq.manager import Manager
from kq.worker import Worker
from kq.queue import Queue
from kq.version import VERSION

__all__ = ['Job', 'Manager', 'Worker', 'Queue', 'VERSION']

# Reduce logging noise from PyKafka
for name, logger in logging.Logger.manager.loggerDict.items():
    if name.startswith('kafka') and isinstance(logger, logging.Logger):
        logger.setLevel(logging.CRITICAL)
