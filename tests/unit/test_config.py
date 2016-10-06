from pytest import raises

from xii import config, error

from fake.open import fake_open, fake_invalid_open


sample_values = {
        "default_host": "qemu://system",
        "parallel": True,
        "parallel_workers": 3,
        "retry_after": 17,
        "ssh_retry": 13,
        "ip_retry": 20
}


def test_config_get():
    test = config.Config(sample_values)
    
    assert(test.get("retry_after") == 17)
    assert(test.get("ssh_retry") == 13)
    assert(test.get("ip_retry") == 20)
    assert(test.get("foo", 42) == 42)


def test_config_default_host():
    test = config.Config(sample_values)
    assert(test.default_host() == "qemu://system")


def test_config_workers():
    test = config.Config(sample_values)
    assert(test.workers() == 3)


def test_config_wait():
    test = config.Config(sample_values)
    assert(test.wait() == 17)


def test_config_retry():
    test = config.Config(sample_values)
    assert(test.retry("ssh") == 13)


def test_load_from_file_valid(monkeypatch, data):
    yaml = data.load("test_config_sample.yml")    
    monkeypatch.setattr("__builtin__.open", fake_open(yaml, "/tmp/xii/config", "r"))

    test = config.load_from_file("/tmp/xii/config")
    assert(test.get("foo") == "bar")
    assert(test.get("auto_delete_volumes") is True)
    assert(test.get("not_existing") is None)


def test_load_from_file_invalid(monkeypatch, data):
    monkeypatch.setattr("__builtin__.open", fake_invalid_open())

    with raises(error.ConnError):
        config.load_from_file("/tmp/xii/config")

    
def test_load_from_file_invalid_yaml(monkeypatch, data):
    yaml = data.load("test_config_sample_invalid.yml")    
    monkeypatch.setattr("__builtin__.open", fake_open(yaml, "/tmp/xii/config", "r"))

    with raises(error.ValidatorError):
        config.load_from_file("/tmp/xii/config") 
