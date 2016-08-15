from xii.attribute import Attribute
from xii.validator import Dict, String, Required, Key


class IPv6Attribute(Attribute):
    entity = "ipv6"

    needs = ["network"]

    defaults = False

    keys = String()

    def info(self):
        pass

    def spawn(self):
        pass


IPv6Attribute.register()
