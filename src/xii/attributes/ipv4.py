from xii.attribute import Attribute
from xii.validator import Dict, String, Key, Required
from xii.output import show_setting


class IPv4Attribute(Attribute):
    attr_name = "ipv4"
    allowed_components = "network"
    defaults = {}

    keys = Dict([
        Required(Key('ip', String())),
        Required(Key('dhcp', Dict([
            Required(Key('start', String())),
            Required(Key('end', String()))
            ]))),
        ])

    def info(self):
        pass

    def spawn(self):
        pass


IPv4Attribute.register()
