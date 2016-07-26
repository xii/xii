
from xii import attribute, paths
from xii.attribute import Key
from xii.output import show_setting


class IPv6Attribute(attribute.Attribute):
    allowed_components = "network"
    defaults = False

    keys = Key.Bool

    def info(self):
        pass

    def spawn(self):
        pass


attribute.Register.register("ipv6", IPv6Attribute)
