from xii import paths, error
from xii.attribute import Attribute
from xii.validator import String
from xii.output import show_setting, info


class NetworkAttribute(Attribute):
    attr_name = "network"
    allowed_components = "node"
    defaults = 'default'

    keys = String()

    def __init__(self, settings, cmpnt):
        Attribute.__init__(self, settings, cmpnt)

    def info(self):
        show_setting('network', self.settings)

    def start(self):
        network = self.conn().get_network(self.settings)

        if not network.isActive():
            info("Starting network {}".format(self.settings))
            network.create()

    def spawn(self):
        network = self.conn().get_network(self.settings)
        if not network:
            raise error.DoesNotExist("Network {} for domain "
                                     "{}".format(self.settings, self.name))

        if not network.isActive():
            info("Starting network {}".format(self.settings))
            network.create()

        self.cmpnt.add_xml('devices', self._gen_xml())

    def _gen_xml(self):
        xml = paths.template('network.xml')
        return xml.safe_substitute({'network': self.settings})


NetworkAttribute.register()
