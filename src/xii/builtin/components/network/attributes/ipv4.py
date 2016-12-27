from xii import paths
from xii.validator import Dict, String, Key, Required


from base import NetworkAttribute


class IPv4Attribute(NetworkAttribute):
    atype = "ipv4"

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
            'ip': self.get('ip', '192.168.122.1'),
            'netmask': self.get('netmask', '255.255.255.0'),
            'start': self.get('dhcp/start', '192.168.122.2'),
            'end': self.get('dhcp/end', '192.168.122.254')
        }
        self.say("setup ipv4 network")
        self.say("gateway ip = {}".format(settings["ip"]))
        self.say("dhcp       = {}/{}".format(settings["start"], settings["end"]))
        xml = paths.template('ipv4.xml')
        self.add_xml(xml.safe_substitute(settings))


IPv4Attribute.register()
