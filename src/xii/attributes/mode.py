
from xii import attribute, paths
from xii.attribute import Key
from xii.output import show_setting


class ModeAttribute(attribute.Attribute):
    allowed_components = "network"
    defaults = None

    keys = Key.Bool

    def info(self):
        pass

    def spawn(self):
        pass


attribute.Register.register("mode", ModeAttribute)
