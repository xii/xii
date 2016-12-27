
from xii.attribute import Attribute
from xii.entity import EntityRegister


class NetworkAttribute(Attribute):

    @classmethod
    def register(cls):
        EntityRegister.register_attribute("network", cls)

    def add_xml(self, xml):
        self.parent().add_xml(xml)
