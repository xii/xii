from xii import paths, error
from xii.need import NeedLibvirt
from xii.attribute import Attribute
from xii.validator import String


class NetworkAttribute(Attribute, NeedLibvirt):
    entity = "network"
    needs = ["node"]
    defaults = 'default'

    keys = String()

    def prepare(self):
        self.add_info("network", self.settings)

    def start(self):
        network = self.get_network(self.settings)

        if network.isActive():
            return

        self.say("starting network {}...".format(self.settings))
        network.create()
        self.success("network {} started!".format(self.settings))

    def spawn(self):
        network = self.get_network(self.settings)
        if not network:
            raise error.NotFound("Network {} for domain "
                                 "{}".format(self.settings, self.name))

        if not network.isActive():
            self.start()

        self.get_parent().add_xml('devices', self._gen_xml())

    def _gen_xml(self):
        xml = paths.template('network.xml')
        return xml.safe_substitute({'network': self.settings})


NetworkAttribute.register()
