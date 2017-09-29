import libvirt
import xml.etree.ElementTree as etree

from time import sleep

from xii import error, need
from xii.validator import String, Or, Dict, RequiredKey, Ip

from xii.components.node import NodeAttribute


class NetworkAttribute(NodeAttribute, need.NeedLibvirt):
    atype = "network"
    defaults = "default"

    keys = Or([
        String("default"),
        Dict([
            RequiredKey("source", String("default")),
            RequiredKey("ip", Ip("192.168.124.87"))
            ])
        ])

    def network_name(self):
        if self._need_ipv4():
            return self.settings("source")
        return self.settings()

    def start(self):
        network = self._get_delayed_network(self.network_name())

        if network.isActive():
            return

        self.say("starting network...")
        network.create()
        self.success("network started!")

    def after_start(self):
        network = self._get_delayed_network(self.network_name())

        if self._need_ipv4():
            mac = self._get_mac_address()
            self._remove_mac(network, mac, self.settings("ip"))
            self._announce_static_ip(network, mac, self.settings("ip"))

    def stop(self):
        network = self._get_delayed_network(self.network_name())

        if self._need_ipv4():
            mac = self._get_mac_address()
            self._remove_mac(network, mac, self.settings("ip"))

    def spawn(self):
        network = self._get_delayed_network(self.network_name())
        if not network:
            raise error.NotFound("Network {} for domain "
                                 "{}".format(self.network_name(), self.component_entity()))

        if not network.isActive():
            self.start()

        self.add_xml('devices', self._gen_xml())

    def _gen_xml(self):
        xml = self.template('network.xml')
        return xml.safe_substitute({'network': self.network_name()})

    def _get_mac_address(self):
        def _uses_network(iface):
            return iface.find("source").attrib["network"] == self.network_name()

        node    = self.get_domain(self.component_entity())
        desc    = etree.fromstring(node.XMLDesc())

        ifaces  = filter(_uses_network, desc.findall("devices/interface"))

        if len(ifaces) == 0:
            raise error.NotFound("Could not find domain interface")

        # FIXME: Add multiple interface support
        #        When multiple interfaces using the same network

        mac = ifaces[0].find("mac")

        if mac is None:
            raise error.NotFound("Could not find interface mac address")

        return mac.attrib["address"]

    def _need_ipv4(self):
        return isinstance(self.settings(), dict)

    def _announce_static_ip(self, network, mac, ip):
        command  = libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST
        flags    = (libvirt.VIR_NETWORK_UPDATE_AFFECT_CONFIG |
                    libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE)
        section  = libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST
        xml      = "<host mac='{}' name='{}' ip='{}' />".format(mac, "xii-" + self.component_entity(), ip)

        try:
            network.update(command, section, -1, xml, flags)
        except libvirt.libvirtError:
            return False
        return True

    def _remove_mac(self, network, mac, ip):
        command  = libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE
        flags    = (libvirt.VIR_NETWORK_UPDATE_AFFECT_CONFIG |
                    libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE)
        section  = libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST
        xml      = "<host mac='{}' name='{}' ip='{}' />".format(mac, "xii-" + self.component_entity(), ip)

        try:
            network.update(command, section, -1, xml, flags)
        except libvirt.libvirtError:
            return False
        return True

    def _get_delayed_network(self, name):
        network = self.get_network(name, raise_exception=False)

        if not network:
            if not self.has_component("network", name):
                raise error.NotFound("Could not find network ({})"
                                     .format(name))
            # wait for network to become ready
            for _ in range(self.global_get("global/retry_network", 20)):
                network = self.get_network(name, raise_exception=False)

                if network:
                    return network
                sleep(self.global_get("global/wait", 3))

            raise error.ExecError("Network {} has not become ready in "
                                  "time. Giving up".format(name))
        return network
