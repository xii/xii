from time import sleep

from xii import paths, error, need
from xii.validator import String

from base import NodeAttribute

class NetworkAttribute(NodeAttribute, need.NeedLibvirt):
    atype = "network"
    defaults = 'default'

    keys = String()

    def start(self):
        network = self._get_delayed_network(self.settings)

        if network.isActive():
            return

        self.say("starting network...")
        network.create()
        self.success("network started!")

    def spawn(self):
        network = self._get_delayed_network(self.settings)
        if not network:
            raise error.NotFound("Network {} for domain "
                                 "{}".format(self.settings, self.component_name()))

        if not network.isActive():
            self.start()

        self.get_parent().add_xml('devices', self._gen_xml())

    def _gen_xml(self):
        xml = paths.template('network.xml')
        return xml.safe_substitute({'network': self.settings})

    def _get_delayed_network(self, name):
        network = self.get_network(name, raise_exception=False)

        if not network:
            is_created = self.get_definition().item(name,
                                                    item_type="network")
            if not is_created:
                raise error.NotFound("Could not find network ({})"
                                     .format(name))
            # wait for network to become ready
            for _ in range(self.get_config().retry("network")):
                network = self.get_network(name, raise_exception=False)

                if network:
                    return network
                sleep(self.get_config().wait())

            raise error.ExecError("Network {} has not become ready in "
                                  "time. Giving up".format(name))
        return network


NetworkAttribute.register()
