from xii.attribute import Attribute
from xii.entity import EntityRegister


class NodeAttribute(Attribute):

    @classmethod
    def register(cls):
        EntityRegister.register_attribute("node", cls)

    def get_tmp_volume_path(self):
        return self.other_attribute("image").get_tmp_volume_path()

    def add_xml(self, section, xml):
        self.parent().add_xml(section, xml)
