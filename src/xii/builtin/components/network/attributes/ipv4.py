from xii import paths
from xii.attributes.base import NetworkAttribute
from xii.validator import Dict, String, Key, Required


class IPv4Attribute(NetworkAttribute):
    entity = "ipv4"

    needs = ["network"]

    defaults = {}

    keys = Dict([
        Required(Key('ip', String())),
        Key('netmask', String()),
        Key('dhcp', Dict([
            Required(Key('start', String())),
            Required(Key('end', String()))
            ])),
        ])

    def spawn(self):
        settings = {
            'ip': self.setting('ip', '192.168.122.1'),
            'netmask': self.setting('netmask', '255.255.255.0'),
            'start': self.setting('dhcp/start', '192.168.122.2'),
            'end': self.setting('dhcp/end', '192.168.122.254')
        }
        self.say("setup ipv4 network")
        self.say("gateway ip = {}".format(settings["ip"]))
        self.say("dhcp       = {}/{}".format(settings["start"], settings["end"]))
        xml = paths.template('ipv4.xml')
        self.get_parent().add_xml(xml.safe_substitute(settings))


IPv4Attribute.register()
