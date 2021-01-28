from pkg_resources import get_distribution

from kq.job import Job
from kq.message import Message
from kq.queue import Queue
from kq.worker import Worker

__version__ = get_distribution("kq").version
