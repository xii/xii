from pytest import raises

from xii import entity, error

import factories


def test_init():
    e = factories.EntityWithStore(name="init")
    assert(e.entity() == "init")

def test_has_parent():
    p = factories.EntityWithStore()
    c = factories.Entity(parent=p)

    assert(c.has_parent() == True)

def test_entity_path():
    p = factories.EntityWithStore()
    c = factories.Entity(parent=p)

    assert(c.entity_path() == [p.entity(), c.entity()])

def test_entity():
    e = factories.EntityWithStore(name="test")
    assert(e.entity() == "test")

def test_store():
    s = factories.StoreWithNode()
    e = factories.Entity(store=s)

    assert(e.store() == s)

def test_config():
    st = factories.StoreWithNode()
    pa = factories.EntityWithStore(store=st)
    ch = factories.Entity(parent=pa)
    c2 = factories.Entity(parent=ch)

    assert(pa.config("image") == st.get("image"))
    assert(ch.config("image") == st.get("image"))
    assert(c2.config("image") == st.get("image"))

def test_add_child():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa._childs == [a, b, c])

def test_validate():

    pa  = factories.EntityWithStore()
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    pa.validate(["a", "b", "c"])

    with raises(error.NotFound):
        pa.validate(["a", "b", "d"])


def test_share():
    pa  = factories.EntityWithStore()

    def mock_creator():
        return "sample"

    def mock_finalizer(value):
        assert(value == "sample")

    result = pa.share("foo", mock_creator, mock_finalizer)
    assert(result == "sample")
    assert(pa.share("foo", mock_creator, mock_finalizer) == "sample")

def test_finalize(capsys):
    pa  = factories.EntityWithStore()

    def mock_creator():
        return "sample"

    def mock_finalizer(value):
        print("test_finalizer_called")
        assert(value == "sample")

    pa.share("foo", mock_creator, mock_finalizer)
    pa.finalize()
    out, _ = capsys.readouterr()
    assert("test_finalizer_called" in out)

def test_run(capsys):
    class Test(entity.Entity):
        def test(self):
            print("test-{}".format(self.entity()))

    t = Test(name="t")
    t.run("test")
    out, _ = capsys.readouterr()
    assert("test-t" in out)

def test_get_child():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa.get_child("a") == a)
    assert(pa.get_child("b") == b)
    assert(pa.get_child("c") == c)
    assert(pa.get_child("d") == None)

def test_children():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    assert(pa.children() == [])

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa.children() == [a, b, c])

def test_each_child():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa.each_child("entity") == ["a", "b", "c"])
    assert(pa.each_child("entity", reverse=True) == ["c", "b", "a"])

def test_child_index():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    b  = factories.Entity(name="b", parent=pa)
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa.child_index("b") == 1)
    assert(pa.child_index("x") == None)

def test_reorder_childs():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    a.requires = ["c"]
    b  = factories.Entity(name="b", parent=pa)
    b.requires = ["a"]
    c  = factories.Entity(name="c", parent=pa)

    pa.add_child(a)
    pa.add_child(b)
    pa.add_child(c)

    assert(pa.children() == [a, b , c])
    pa.reorder_childs()
    assert(pa.children() == [c, a , b])


def test_reorder_childs_cycle():
    pa  = factories.EntityWithStore(name="pa")
    a  = factories.Entity(name="a", parent=pa)
    a.requires = ["b"]
    b  = factories.Entity(name="b", parent=pa)
    b.requires = ["a"]

    pa.add_child(a)
    pa.add_child(b)

    assert(pa.children() == [a, b])

    with raises(error.Bug):
        pa.reorder_childs()
