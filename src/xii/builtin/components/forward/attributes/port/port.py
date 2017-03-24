from libvirt import libvirtError
from xii.validator import Int, List, Dict, Key, RequiredKey, Or, String, VariableKeys
from xii import need, error, util

from xii.components.forward import ForwardAttribute


class PortAttribute(ForwardAttribute, need.NeedLibvirt):
    atype = "port"
    keys = Dict([VariableKeys(
            List(
                Dict([
                    RequiredKey("guest-port", Int("80")),
                    RequiredKey("host-port", Int("8080")),
                    Key("proto", String("tcp")),
                    Key("host-ip", String("192.168.127.122")),
                    Key("interface", String("vibr0"))
                ])
            )
        , "webservers")
    ])

    def forwards_for(self, instance):
        result = []

        for inst, forwards in self.settings().items():
            if inst != instance:
                continue
            for forward in forwards:
                result.append(util.create_xml_node("port", forward))
        return result

    def _get_nodes(self):
        return self.settings().keys()

    def _fetch_host_ip(self, instance):
        cmpnt = self.command().get_component(instance)
        network = cmpnt.get_attribute("network").network_name()
        return self.network_get_host_ip(network, "ipv4")
