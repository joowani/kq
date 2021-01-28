from setuptools import find_packages, setup

with open("./README.md") as fp:
    description = fp.read()

setup(
    name="kq",
    description="Kafka Job Queue for Python",
    long_description=description,
    long_description_content_type="text/markdown",
    author="Joohwan Oh",
    author_email="joohwan.oh@outlook.com",
    url="https://github.com/joowani/kq",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    license="MIT",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=[
        "dataclasses",
        "dill>=0.3.2",
        "kafka-python>=2.0.0",
        "setuptools>=42",
        "setuptools_scm[toml]>=3.4",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort>=5.0.0",
            "mypy",
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "recommonmark",
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
    ],
)
