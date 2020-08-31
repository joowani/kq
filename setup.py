from setuptools import setup, find_packages

version = {}
with open('./kq/version.py') as fp:
    exec(fp.read(), version)

with open('./README.rst') as fp:
    description = fp.read()

setup(
    name='kq',
    description='Kafka Job Queue for Python',
    version=version['__version__'],
    long_description=description,
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/kq',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    license='MIT',
    install_requires=[
        'dill>=0.3.2',
        'kafka-python>=2.0.0',
    ],
    tests_require=['pytest', 'mock', 'flake8'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring',
    ]
)
