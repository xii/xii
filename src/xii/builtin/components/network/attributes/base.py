
from xii.attribute import Attribute
from xii.entity import EntityRegister


class NetworkAttribute(Attribute):

    @classmethod
    def register(cls):
        EntityRegister.register_attribute("network", cls)
