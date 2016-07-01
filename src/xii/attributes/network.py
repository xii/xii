from xii import attribute, paths, error
from xii.output import show_setting, info


class NetworkAttribute(attribute.Attribute):
    name = "network"
    allowed_components = "node"
    defaults = 'default'

    def __init__(self, value, cmpnt):
        attribute.Attribute.__init__(self, value, cmpnt)
        self.network = self.value

    def info(self):
        show_setting('network', self.network)

    def spawn(self, domain_name):
        if isinstance(self.value, dict):
            self.network = self._fetch_network_name()
            self._prepare_network_interface()

        network = self.conn().get_network(self.value)

        if not network:
            raise error.DoesNotExist("Network {} for domain "
                                     "{}".format(self.value, domain_name))

        if not network.isActive():
            info("Starting network {}".format(self.value))
            network.create()
            
        self.cmpnt.add_xml('devices', self._gen_xml())

    def _fetch_network_name(self):
        pass

    def _prepare_network_interface(self):
        pass

    def _gen_xml(self):
        xml = paths.template('network.xml')
        return xml.safe_substitute({'network': self.network})


attribute.Register.register('network', NetworkAttribute)
