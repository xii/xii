import libvirt
from time import time

from xii.component import Component
from xii.need import NeedLibvirt, NeedIO
from xii import error, util


class NetworkComponent(Component, NeedLibvirt, NeedIO):
    ctype = "network"

    required_attributes = ["stay", "mode"]
    default_attributes = ["stay"]

    xml_net = []

    def add_xml(self, xml):
        self.xml_net.append(xml)

    def fetch_metadata(self):
        return self.fetch_resource_metadata("network", self.entity())

    def spawn(self):
        network = self.get_network(self.entity(), raise_exception=False)

        if network is not None:
            return

        self.add_meta({
            "created" : time(),
            "definition": self.config("runtime/definition"),
            "user": self.io().user()
            })

        self.say("creating...")
        self.each_attribute("spawn")

        replace = {
            "config": "\n".join(self.xml_net),
            "name": self.entity(),
            "meta": self.meta_to_xml()
            }

        import pdb; pdb.set_trace()

        tpl = self.template("network.xml")
        xml = tpl.safe_substitute(replace)

        # FIXME: Handle case where the network already is used by another
        # device
        try:
            self.virt().networkDefineXML(xml)
            net = self.get_network(self.entity())
            self.success("created!")
            return net
        except libvirt.libvirtError as err:
            raise error.ExecError("Could not define {}: {}"
                                  .format(self.entity(), err))

    def start(self):
        self.say("starting...")
        net = self.get_network(self.entity())

        self.each_attribute("start")

        if net.isActive():
            self.say("is already started")
            return True

        net.create()

        # cleanup environment
        self.finalize()

        if not util.wait_until_active(net):
            self.warn("could not start network")
            return False

        self.success("network started!")

    def stop(self):
        self.say("stopping...")
        net = self.get_network(self.entity(), raise_exception=False)

        if not net:
            self.warn("does not exist")
            return

        self._stop_network(net)

    def destroy(self):
        net = self.get_network(self.entity(), raise_exception=False)

        if not net:
            self.warn("does not exist")
            return

        if net.isActive():
            self._stop_network(net)

        self.each_attribute("destroy")

        net.undefine()
        self.success("removed!")

    def _stop_network(self, net):
        self.say("stopping...")
        self.each_attribute("stop")

        if not net.isActive():
            self.say("is already stopped")
            return

        net.destroy()

        if not util.wait_until_inactive(net):
            self.warn("could not stop network")
            return
        self.success("stopped!")
        return
