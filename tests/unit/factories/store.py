import factory
from xii.store import Store

from fixtures import load_fixture

class StoreFactory(factory.Factory):
    class Meta:
        model = Store
    parent = {}

class StoreWithNode(StoreFactory):
    parent = factory.LazyAttribute(lambda _: load_fixture("store_with_node"))

class StoreWithRawNode(StoreFactory):
    parent = factory.LazyAttribute(lambda _: load_fixture("store_with_raw_node"))


