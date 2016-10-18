"""
KQ (Kafka Queue) command line tool

Usage:
  kq (worker|info) [--hosts=<hosts>]
                   [--topic=<topic>]
                   [--timeout=<timeout>]
                   [--callback=<callback>]
                   [--job-size=<job-size>]
                   [--cafile=<cafile>]
                   [--certfile=<certfile>]
                   [--keyfile=<keyfile>]
                   [--crlfile=<crlfile>]
                   [--verbose]
  kq --help
  kq --version

Options:
  --hosts=<hosts>        Comma-separated Kafka hosts [default: 127.0.0.1]
  --topic=<topic>        Name of the Kafka topic [default: default]
  --job-size=<job-size>  Maximum job size in bytes [default: 1048576]
  --timeout=<timeout>    Job timeout threshold in seconds
  --callback=<callback>  Python module containing the callback function
  --cafile=<cafile>      Full path to SSL trusted CA certificate
  --certfile=<certfile>  Full path to SSL client certificate
  --keyfile=<keyfile>    Full path to SSL private key
  --crlfile=<crlfile>    Full path to SSL crlfile for verifying expiry
  --verbose              Turn on debug logging output
  --help                 Display this help menu
  --version              Display the version of KQ

"""

import os
import sys
import logging

import docopt

import kq


def entry_point():
    args = docopt.docopt(__doc__, version=kq.VERSION)

    # Set up the logger
    logger = logging.getLogger('kq')
    if args['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
    ))
    logger.addHandler(stream_handler)

    # Import the callback function if given
    callback = None
    if args['--callback']:  # pragma: no cover
        try:
            path = os.path.abspath(
                os.path.expanduser(args['--callback'])
            )
            if sys.version_info.major == 2:
                import imp
                module = imp.load_source('kqconfig', path)
            elif sys.version_info.minor < 5:
                from importlib.machinery import SourceFileLoader as Loader
                module = Loader('kqconfig', path).load_module()
            else:
                from importlib import util
                spec = util.spec_from_file_location("kqconfig", path)
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)
            callback = getattr(module, 'callback')
        except Exception as e:
            logger.exception('Failed to load callback: {}'.format(e))

    if args['info']:
        kq.Manager(
            hosts=args['--hosts'],
            cafile=args['--cafile'],
            certfile=args['--certfile'],
            keyfile=args['--keyfile'],
            crlfile=args['--crlfile'],
        ).info()

    elif args['worker']:
        timeout = args['--timeout']
        kq.Worker(
            hosts=args['--hosts'],
            topic=args['--topic'],
            timeout=int(timeout) if timeout else None,
            callback=callback,
            job_size=int(args['--job-size']),
            cafile=args['--cafile'],
            certfile=args['--certfile'],
            keyfile=args['--keyfile'],
            crlfile=args['--crlfile'],
        ).start()
