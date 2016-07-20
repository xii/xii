
from xii import attribute, paths
from xii.attribute import Key
from xii.output import show_setting


class GraphicAttribute(attribute.Attribute):
    name = "graphic"
    allowed_components = "node"
    defaults = None

    keys = Key.Bool

    def info(self):
        if self.settings:
            show_setting("graphic", "enabled")

    def spawn(self, _):
        if not self.settings:
            return

        xml = paths.template('graphic.xml')
        self.cmpnt.add_xml('devices', xml.safe_substitute())


attribute.Register.register("graphic", GraphicAttribute)
