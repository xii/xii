from xii.components.network import NetworkAttribute
from xii.validator import Dict, String, Key, RequiredKey, Ip


class IPAttribute(NetworkAttribute):

    keys = Dict([
        RequiredKey("ip", Ip("192.168.124.1")),
        Key("netmask", String("255.255.255.0")),
        Key("dhcp", Dict([
            RequiredKey("start", Ip("192.168.124.2")),
            RequiredKey("end", Ip("192.168.124.254"))
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
        xml = self.template(self.atype + ".xml")
        self.add_xml(xml.safe_substitute(settings))

class IPv4Attribute(IPAttribute):
    atype = "ipv4"
    default_netmask = "255.255.255.0"

class IPv6Attribute(IPAttribute):
    atype = "ipv6"
    default_netmask = "64"
