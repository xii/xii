from xii.attribute import Attribute


class NetworkAttribute(Attribute):

    def add_xml(self, xml):
        self.parent().add_xml(xml)
