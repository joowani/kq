from kq.version import __version__


def test_version():
    assert isinstance(__version__, str)

    version_parts = __version__.split('.')
    assert len(version_parts) == 3
    assert all(part.isdigit() for part in version_parts)
