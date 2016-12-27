from xii.validator import Dict, String, Required, Key


from base import NetworkAttribute


class IPv6Attribute(NetworkAttribute):
    atype = "ipv6"

    defaults = False

    keys = String()

    def spawn(self):
        pass


IPv6Attribute.register()
