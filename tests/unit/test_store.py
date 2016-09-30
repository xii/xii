from pytest import raises


from xii import store


sample = {
    "foo" : "bar",
    "baz" : "buz",
    "struct": {
        "one" : 1,
        "two" : 2,
        "three": 3
    },
    "array": [1, 2, 3, 4]
}



def test_create_store():
    assert(store.Store() is not None)
    assert(store.Store(parent={"foo": "bar"}) is not None)


def test_get_store():
    test = store.Store(parent=sample)

    assert(test.get("foo") == "bar")
    assert(test.get("struct/two") == 2)


def test_set_store():
    test = store.Store()

    test.set("foo", {})
    test.set("foo/bar", 2)

    assert(test.get("foo/bar") == 2)


def test_derive_store():
    test = store.Store(parent = {"foo": {}})
    derive = test.derive("foo")

    derive.set("bar", 42)

    assert(derive.get("bar") == 42)
    assert(test.get("foo/bar") == 42)
