from xii.attributes.base import NetworkAttribute
from xii.validator import Dict, String, Required, Key


class IPv6Attribute(NetworkAttribute):
    entity = "ipv6"

    needs = ["network"]

    defaults = False

    keys = String()

    def info(self):
        pass

    def spawn(self):
        pass


IPv6Attribute.register()
