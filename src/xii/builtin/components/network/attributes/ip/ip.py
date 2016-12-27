from xii import paths
from xii.attribute import Attribute
from xii.validator import Dict, String, Key, Required, Ip

import foobar

class IPAttribute(Attribute):

    keys = Dict([
        Required(Key("ip", Ip())),
        Key("netmask", String()),
        Key("dhcp", Dict([
            Required(Key("start", Ip())),
            Required(Key("end", Ip()))
            ])),
        ])

    def spawn(self):
        settings = {
            "family": self.atype,
            "ip": self.settings("ip"),
            "netmask": self.settings("netmask", self.default_netmask),
            "start": self.settings("dhcp/start"),
            "end": self.settings("dhcp/end")
        }
        xml = paths.template(self.atype + ".xml")
        self.add_xml(xml.safe_substitute(settings))

class IPv4Attribute(IPAttribute):
    atype = "ipv4"
    default_netmask = "255.255.255.0"

class IPv6Attribute(IPAttribute):
    atype = "ipv6"
    default_netmask = "64"
