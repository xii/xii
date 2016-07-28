
from xii import paths
from xii.attribute import Attribute
from xii.validator import Bool
from xii.output import show_setting


class GraphicAttribute(Attribute):
    attr_name = "graphic"
    allowed_components = "node"
    defaults = None

    keys = Bool()

    def info(self):
        if self.settings:
            show_setting("graphic", "enabled")

    def spawn(self):
        if not self.settings:
            return

        xml = paths.template('graphic.xml')
        self.cmpnt.add_xml('devices', xml.safe_substitute())


GraphicAttribute.register()
