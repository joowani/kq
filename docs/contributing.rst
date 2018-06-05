Contributing
------------

Requirements
============

Before submitting a pull request on GitHub_, please make sure you meet the
following requirements:

* The pull request points to dev_ branch.
* Changes are squashed into a single commit. I like to use git rebase for this.
* Commit message is in present tense. For example, "Fix bug" is good while
  "Fixed bug" is not.
* Sphinx_-compatible docstrings.
* PEP8_ compliance.
* No missing docstrings or commented-out lines.
* Test coverage_ remains at %100. If a piece of code is trivial and does not
  need unit tests, use this_ to exclude it from coverage.
* No build failures on `Travis CI`_. Builds automatically trigger on pull
  request submissions.
* Documentation is kept up-to-date with the new changes (see below).

.. warning::
    The dev branch is occasionally rebased, and its commit history may be
    overwritten in the process. Before you begin your feature work, git fetch
    or pull to ensure that your local branch has not diverged. If you see git
    conflicts and want to start with a clean slate, run the following commands:

    .. code-block:: bash

        ~$ git checkout dev
        ~$ git fetch origin
        ~$ git reset --hard origin/dev  # THIS WILL WIPE ALL LOCAL CHANGES

Style
=====

To ensure PEP8_ compliance, run flake8_:

.. code-block:: bash

    ~$ pip install flake8
    ~$ git clone https://github.com/joowani/kq.git
    ~$ cd kq
    ~$ flake8

If there is a good reason to ignore a warning, see here_ on how to exclude it.

Testing
=======

To test your changes, you can run the integration test suite that comes with
**kq**. It uses pytest_ and requires an actual Kafka instance.

To run the test suite (use your own Kafka broker host and port):

.. code-block:: bash

    ~$ pip install pytest
    ~$ git clone https://github.com/joowani/kq.git
    ~$ cd kq
    ~$ py.test -v -s --host=127.0.0.1 --port=9092

To run the test suite with coverage report:

.. code-block:: bash

    ~$ pip install coverage pytest pytest-cov
    ~$ git clone https://github.com/joowani/kq.git
    ~$ cd kq
    ~$ py.test -v -s --host=127.0.0.1 --port=9092 --cov=kq

As the test suite creates real topics and messages, it should only be run in
development environments.

Documentation
=============

The documentation including the README is written in reStructuredText_ and uses
Sphinx_. To build an HTML version on your local machine:

.. code-block:: bash

    ~$ pip install sphinx sphinx_rtd_theme
    ~$ git clone https://github.com/joowani/kq.git
    ~$ cd kq/docs
    ~$ sphinx-build . build  # Open build/index.html in a browser

As always, thank you for your contribution!

.. _dev: https://github.com/joowani/kq/tree/dev
.. _GitHub: https://github.com/joowani/kq
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _coverage: https://coveralls.io/github/joowani/kq
.. _this: http://coverage.readthedocs.io/en/latest/excluding.html
.. _Travis CI: https://travis-ci.org/joowani/kq
.. _Sphinx: https://github.com/sphinx-doc/sphinx
.. _flake8: http://flake8.pycqa.org
.. _here: http://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors
.. _pytest: https://github.com/pytest-dev/pytest
.. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
