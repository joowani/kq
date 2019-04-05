from setuptools import setup, find_packages

version = {}
with open('./kq/version.py') as fp:
    exec(fp.read(), version)

setup(
    name='kq',
    description='Kafka Job Queue for Python',
    version=version['VERSION'],
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/kq',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'dill>=0.2.5',
        'docopt>=0.6.2',
        'kafka-python==1.3.5'
    ],
    entry_points={
        'console_scripts': [
            'kq = kq.cli:entry_point',
        ],
    },
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring',
    ]
)
