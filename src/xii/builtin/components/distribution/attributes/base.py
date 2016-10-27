from xii.attribute import Attribute
from xii.entity import EntityRegister


class DistAttribute(Attribute):

    @classmethod
    def register(cls):
        EntityRegister.register_attribute("distribution", cls)
