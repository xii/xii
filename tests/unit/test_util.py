import io
from pytest import raises, xfail

from fake.open import fake_open, fake_invalid_open

from xii import util, error


def test_safe_get():
    assert(util.safe_get("foo", {"foo": 1}) == 1)
    assert(util.safe_get("bar", {"foo": 1}) is None)


def test_file_read(monkeypatch):

    monkeypatch.setattr("__builtin__.open", fake_open(u"test stream", "/tmp/test", "r"))
    assert(util.file_read("/tmp/test") == "test stream")


def test_file_read_invalid(monkeypatch):
    monkeypatch.setattr("os.open", fake_invalid_open())

    with raises(error.NotFound):
        util.file_read("/invalid/directory/file")


def test_make_temp_name(monkeypatch):
    monkeypatch.setattr("time.time", lambda: 12345678)

    assert(util.make_temp_name("foo") == "/tmp/xii-42313019c69cd1d99159b3518037f557")


def test_yaml_read(monkeypatch, data):
    yaml = data.load("test_util_sample.yaml")

    monkeypatch.setattr("__builtin__.open", fake_open(yaml, "/tmp/yaml", "r"))

    result = util.yaml_read("/tmp/yaml")
    
    assert(result["multiple"]["network"] == "default")


def test_yaml_read_invalid(monkeypatch, data):
    yaml = data.load("test_util_sample_invalid.yaml")

    monkeypatch.setattr("__builtin__.open", fake_open(yaml, "/tmp/yaml", "r"))
    
    with raises(error.ValidatorError):
        util.yaml_read("/tmp/yaml")


def test_yaml_read_ioerror(monkeypatch):

    monkeypatch.setattr("__builtin__.open", fake_invalid_open())
    
    with raises(error.DefError):
        util.yaml_read("/tmp/yaml")


class FakeObject():
    def __init__(self, count):
        self._count = count

    def isActive(self):
        if self._count == 0:
            return True
        
        self._count -= 1
        return False

def test_wait_until_active(sleep):
    sleep.set_sleep_time(1)
    
    util.wait_until_active(FakeObject(3))

    assert(sleep.call_count() == 3)





   

