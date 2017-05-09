.. _command-line-tool:

Command Line Tool
-----------------

KQ comes with a command line tool ``kq`` that let's you quickly spawn workers
or view the offsets on topic partitions:

.. code-block:: bash

    ~$ kq --help

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
                       [--proc-ttl=<proc-ttl>]
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
      --proc-ttl=<proc-ttl>  Records read before re-spawning process [default: 5000]
      --verbose              Turn on debug logging output
      --help                 Display this help menu
      --version              Display the version of KQ
