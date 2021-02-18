# Contributing

Set up dev environment:
```shell
cd ~/your/repository/fork  # Activate venv if you have one (recommended)
pip install -e .[dev]      # Install dev dependencies (e.g. black, mypy, pre-commit)
pre-commit install         # Install git pre-commit hooks
```

Run unit tests with coverage:

```shell
docker run -d -p 9092:9092 -e ADV_HOST=127.0.0.1 lensesio/fast-data-dev  # Start Kafka docker.
py.test --cov=kq --cov-report=html  # Open htmlcov/index.html in your browser
```

Build and test documentation:

```shell
python -m sphinx docs docs/_build  # Open docs/_build/index.html in your browser
```

Thank you for your contribution!
