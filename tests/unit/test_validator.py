from pytest import raises

from xii import validator, error


def expect_verified_type(sample_klass, sample, failing_sample=None):
    assert(sample_klass.validate("expect_verified_type", sample) is True)

    with raises(error.ValidatorError):
        sample_klass.validate("expect_verified_type", failing_sample)


def test_type_check():
    simple = validator.TypeCheck()
    simple.want = "int"
    simple.want_type = int
    assert(simple.validate("test_type_check", 3) is True)

    with raises(error.ValidatorError):
        simple.validate("test_type_check", "foo")


def test_int():
    expect_verified_type(validator.Int(), 3, "not an int")


def test_bool():
    expect_verified_type(validator.Bool(), True, 3)


def test_string():
    expect_verified_type(validator.String(), "a string", None)


def test_ip():
    expect_verified_type(validator.Ip(), "127.0.0.1", 127)

    ip_validator = validator.Ip()

    assert(ip_validator.validate("test_ip", "127.0.0.1") is True)
    assert(ip_validator.validate("test_ip", "255.255.255.255") is True)

    with raises(error.ValidatorError):
        ip_validator.validate("test_ip", "some.hostname.com")

    with raises(error.ValidatorError):
        ip_validator.validate("test_ip", "google.com")

    with raises(error.ValidatorError):
        ip_validator.validate("test_ip", "800.800.800.800")

    with raises(error.ValidatorError):
        ip_validator.validate("test_ip", "1.2.3")

    with raises(error.ValidatorError):
        ip_validator.validate("test_ip", "")


def test_list():
    test = validator.List(validator.Int())

    expect_verified_type(test, [1,2,3], {})

    assert(test.validate("test_list", [1, 2, 3]) is True)
    assert(test.validate("test_list", []) is False)

    with raises(error.ValidatorError):
        test.validate("test_list", [1, 2, 3, "4", 5])


def test_dict():
    test = validator.Dict([
        validator.RequiredKey("foo", validator.Int()),
        validator.Key("bar", validator.String())
    ])

    expect_verified_type(test, {"foo": 1}, [1, 2, 3])

    assert(test.validate("test_dict", {"foo": 1, "bar": "baz"}) is True)

    with raises(error.ValidatorError):
        test.validate("test_dict", {"bar": 1})



def test_or():
    non_exclusive = validator.Dict([
        validator.Or([
            validator.RequiredKey("foo", validator.Int()),
            validator.RequiredKey("bar", validator.String())
        ], exclusive=False)
    ])
    exclusive = validator.Dict([
        validator.Or([
            validator.Key("foo", validator.Int()),
            validator.Key("bar", validator.String())
        ], exclusive=True)
    ])

    assert(non_exclusive.validate("test_or", {"foo": 1}) is True)
    assert(non_exclusive.validate("test_or", {"bar": "baz"}) is True)
    assert(non_exclusive.validate("test_or", {"foo": 1, "bar": "baz"}) is True)

    assert(exclusive.validate("test_or", {"foo": 1}) is True)
    assert(exclusive.validate("test_or", {"bar": "baz"}) is True)

    with raises(error.ValidatorError):
        exclusive.validate("test_or", {"foo": 1, "bar": "baz"})


def test_key():
    test = validator.Key("bar", validator.Int())

    assert(test.validate("test_key", {}) is False)
    assert(test.validate("test_key", {"foo": 2}) is False)
    assert(test.validate("test_key", {"bar": 3}) is True)

    with raises(error.ValidatorError):
        test.validate("test_key", {"bar": "foo"})


def test_variable_keys():
    test = validator.VariableKeys(validator.String())

    assert(test.validate("test_variable_keys", {"foo": "bar"}) is True)
    assert(test.validate("test_variable_keys", {"baz": "bar"}) is True)

    with raises(error.ValidatorError):
        test.validate("test_variable_keys", {"foo": 1})

def test_required_key():
    check = validator.RequiredKey("test", validator.String())

    assert(check.validate("test_required_key", {"test": "foo"}) is True)

    with raises(error.ValidatorError):
        check.validate("test_required_key", {})

    with raises(error.ValidatorError):
        check.validate("test_required_key", {"test": 1})


