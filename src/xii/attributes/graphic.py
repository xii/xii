
from xii import paths
from xii.attributes.nodeattribute import NodeAttribute
from xii.validator import Bool
from xii.output import show_setting


class GraphicAttribute(NodeAttribute):
    entity = "graphic"

    keys = Bool()

    def prepare(self):
        if not self.settings:
            return
        self.add_info("graphic", "yes")

    def spawn(self):
        if not self.settings:
            return
        xml = paths.template('graphic.xml')
        self.get_parent().add_xml('devices', xml.safe_substitute())


GraphicAttribute.register()
