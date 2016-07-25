from xii import attribute, paths, error
from xii.attribute import Key
from xii.output import show_setting, info


class NetworkAttribute(attribute.Attribute):
    name = "network"
    allowed_components = "node"
    defaults = 'default'

    keys = Key.String

    def __init__(self, settings, cmpnt):
        attribute.Attribute.__init__(self, settings, cmpnt)

    def info(self):
        show_setting('network', self.settings)

    def start(self, _):
        network = self.conn().get_network(self.settings)

        if not network.isActive():
            info("Starting network {}".format(self.settings))
            network.create()

    def spawn(self, domain_name):
        network = self.conn().get_network(self.settings)
        if not network:
            raise error.DoesNotExist("Network {} for domain "
                                     "{}".format(self.settings, domain_name))

        if not network.isActive():
            info("Starting network {}".format(self.settings))
            network.create()

        self.cmpnt.add_xml('devices', self._gen_xml())

    def _gen_xml(self):
        xml = paths.template('network.xml')
        return xml.safe_substitute({'network': self.settings})


attribute.Register.register('network', NetworkAttribute)
