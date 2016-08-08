from xii import paths
from xii.attribute import Attribute
from xii.validator import Dict, String, Key, Required
from xii.output import show_setting


class IPv4Attribute(Attribute):
    entity = "ipv"

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

    def prepare(self):
        self.add_info('host ip (ipv4)', self.settings['ip'])
        if self.setting('dhcp'):
            self.add_info('dhcp (ipv4)', "{} / {}".format(self.setting('dhcp/start'),
                                                          self.setting('dhcp/end')))

    def spawn(self):
        settings = {
            'ip': self.setting('ip', '192.168.122.1'),
            'netmask': self.setting('netmask', '255.255.255.0'),
            'start': self.setting('dhcp/start', '192.168.122.2'),
            'end': self.setting('dhcp/end', '192.168.122.254')
        }
        xml = paths.template('ipv4.xml')
        self.cmpnt.add_xml(xml.safe_substitute(settings))


IPv4Attribute.register()
