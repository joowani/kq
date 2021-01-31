## KQ: Kafka Job Queue for Python

![Build](https://github.com/joowani/kq/workflows/Build/badge.svg)
![CodeQL](https://github.com/joowani/kq/workflows/CodeQL/badge.svg)
[![codecov](https://codecov.io/gh/joowani/kq/branch/main/graph/badge.svg?token=U81CouJF4T)](https://codecov.io/gh/joowani/kq)

**KQ (Kafka Queue)** is a lightweight Python library which lets you queue and
execute jobs asynchronously using [Apache Kafka](https://kafka.apache.org/). It is 
built on top of [kafka-python](https://github.com/dpkp/kafka-python).

### Announcements

* Python 3.5 will not be supported from kq v3.0.0.
* See [releases](https://github.com/joowani/kq/releases) for latest updates.

### Requirements

* [Apache Kafka](https://kafka.apache.org) 0.9+
* Python 3.6+

### Installation

Install using [pip](https://pip.pypa.io):

```shell
pip install kq
```

### Usage

Start your Kafka instance. 
Example using [Kafka Docker](https://github.com/lensesio/fast-data-dev):

```shell
docker run -p 9092:9092 -e ADV_HOST=127.0.0.1 lensesio/fast-data-dev
```

Define your KQ ``worker.py`` module:

```python
import logging

from kafka import KafkaConsumer
from kq import Worker

# Set up logging.
formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger('kq.worker')
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

# Set up a Kafka consumer.
consumer = KafkaConsumer(
    bootstrap_servers='127.0.0.1:9092',
    group_id='group',
    auto_offset_reset='latest'
)

# Set up a worker.
worker = Worker(topic='topic', consumer=consumer)
worker.start()
```

Start your worker:

```shell
python my_worker.py
[INFO] Starting Worker(hosts=127.0.0.1:9092 topic=topic, group=group) ...
```

Enqueue a function call:

```python
import requests

from kafka import KafkaProducer
from kq import Queue

# Set up a Kafka producer.
producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

# Set up a queue.
queue = Queue(topic='topic', producer=producer)

# Enqueue a function call.
job = queue.enqueue(requests.get, 'https://google.com')

# You can also specify the job timeout, Kafka message key and partition.
job = queue.using(timeout=5, key=b'foo', partition=0).enqueue(requests.get, 'https://google.com')
```

The worker executes the job in the background:

```shell
python my_worker.py
[INFO] Starting Worker(hosts=127.0.0.1:9092, topic=topic, group=group) ...
[INFO] Processing Message(topic=topic, partition=0, offset=0) ...
[INFO] Executing job c7bf2359: requests.api.get('https://www.google.com')
[INFO] Job c7bf2359 returned: <Response [200]>
```

See [documentation](https://kq.readthedocs.io) for more information.

### Contributing

Set up dev environment:

```shell
cd ~/your/kq/clone          # Activate venv if you have one
pip install -e .[dev]       # Install dev dependencies (black, mypy, pre-commit etc.)
pre-commit install          # Install git pre-commit hooks
py.test                     # Run unit tests
```

Run unit tests:
```shell
docker run -p 9092:9092 -e ADV_HOST=127.0.0.1 lensesio/fast-data-dev  # Start Kafka docker
py.test
```
