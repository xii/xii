import io
import pytest


class MockedOpen(io.StringIO):
    def __init__(self, content, paths, mode):
        io.StringIO.__init__(self, content)
        self.mode = mode
        self.paths = mode

    def _validate(self, path, mode):
        if mode != self.mode:
            pytest.xfail("[fake][open] mode is not equal ({} should be {})"
                         .format(mode, self.mode))

        if path not in self.paths:
            pytest.xfail("[fake][open] {} is not a known test path"
                         .format(path))

    def __call__(self, path, mode):
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class InvalidMockedOpen():
    def __call__(path, mode, *args, **kwargs):
        raise IOError("invalid open")


def fake_open(content, paths, mode='r'):
    return MockedOpen(content, paths, mode)


def fake_invalid_open():
    return InvalidMockedOpen()
