from xii.attribute import Attribute
from xii.entity import EntityRegister


class NodeAttribute(Attribute):

    @classmethod
    def register(cls):
        EntityRegister.register_attribute("node", cls)

    def get_domain_image_path(self):
        return self.get_parent().get_domain_image_path()
