
from xii import attribute, paths
from xii.output import show_setting


class GraphicAttribute(attribute.Attribute):
    name = "graphic"
    allowed_components = "node"
    defaults = None

    def info(self):
        if self.value:
            show_setting("graphic", "enabled")

    def spawn(self, _):
        if not self.value:
            return

        xml = paths.template('graphic.xml')
        self.cmpnt.add_xml('devices', xml.safe_substitute())


attribute.Register.register("graphic", GraphicAttribute)
