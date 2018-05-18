KQ: Kafka-based Job Queue for Python
------------------------------------

Welcome to the documentation for **KQ (Kafka Queue)**, a lightweight Python
library which lets you queue and execute jobs asynchronously using `Apache Kafka`_.
It uses kafka-python_ under the hood.

Requirements
============

- `Apache Kafka`_ 0.9+
- Python 3.5+

Installation
============

To install a stable version from PyPI_ (recommended):

.. code-block:: bash

    ~$ pip install kq

To install the latest version directly from GitHub_:

.. code-block:: bash

    ~$ pip install -e git+git@github.com:joowani/kq.git@master#egg=kq

You may need to use ``sudo`` depending on your environment.

Contents
========

.. toctree::
    :maxdepth: 1

    overview
    queue
    worker
    job
    message
    callback
    serializer
    logging
    contributing

.. _Apache Kafka: https://kafka.apache.org
.. _kafka-python: https://github.com/dpkp/kafka-python
.. _PyPI: https://pypi.python.org/pypi/kq
.. _GitHub: https://github.com/joowani/kq
