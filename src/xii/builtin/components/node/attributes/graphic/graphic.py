from xii import paths
from xii.validator import Bool

from xii.components.node import NodeAttribute


class GraphicAttribute(NodeAttribute):
    atype = "graphic"

    keys = Bool()

    def spawn(self):
        if not self.settings():
            return
        xml = paths.template('graphic.xml')
        self.add_xml('devices', xml.safe_substitute())
