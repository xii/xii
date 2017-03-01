from libvirt import libvirtError
from xii.validator import Int, List, Dict, VariableKeys
from xii import need, error
from xii.components.forward import ForwardAttribute


class PortAttribute(ForwardAttribute, need.NeedLibvirt):
    atype = "port"
    keys = Dict([
        VariableKeys(Dict([
            VariableKeys(Int("8080"), "80", keytype=Int("80"))
            ]), "instance-1")
        ])

    def forwards_for(self, instance):
        result = []
        host_ip = self._fetch_host_ip(instance)
        tpl = self.template("node-port-forward.xml")

        for inst, forwards in self.settings().items():
            if inst != instance:
                continue
            for source, dest in forwards.items():
                xml = tpl.safe_substitute({
                    "source": dest,
                    "dest": source,
                    "host_ip": host_ip
                })
                result.append(xml)
        return result

    def spawn(self):
        filter = self.get_nwfilter("xii-port-forward", raise_exception=False)

        if filter is not None:
            return

        tpl = self.template("xii-port-forward-filter.xml")

        try:
            xml = tpl.safe_substitute()
            self.virt().nwfilterDefineXML(xml)
        except libvirtError as err:
            raise error.ExecError("Could not create network "
                                  "filter for port forwarding: {}".format(err))

    def _get_nodes(self):
        return self.settings().keys()

    def _fetch_host_ip(self, instance):
        cmpnt = self.command().get_component(instance)
        network = cmpnt.get_attribute("network").network_name()
        return self.network_get_host_ip(network, "ipv4")
