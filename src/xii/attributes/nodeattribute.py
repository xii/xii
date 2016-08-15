
from xii.attribute import Attribute


class NodeAttribute(Attribute):

    needs = ["node"]

    def get_domain_image_path(self):
        return self.get_parent().get_domain_image_path()
