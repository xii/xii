import libvirt

from xii.component import Component
from xii.need import NeedLibvirt
from xii import error, paths, util


class NetworkComponent(Component, NeedLibvirt):
    entity = "network"

    defaults = ['stay']
    requires = ['mode']

    xml_net = []

    def add_xml(self, xml):
        self.xml_net.append(xml)

    def start(self):
        net = self.get_network(self.name, raise_exception=False)

        if not net:
            net = self._spawn_network()

        self.childs_run("start")

        if net.isActive():
            self.say("is already started")
            return True

        net.create()

        # cleanup environment
        self.finalize()

        if not util.wait_until_active(net):
            self.warn("could not start network")
            return False

        self.success("network started")


    def stop(self):
        net = self.get_network(self.name, raise_exception=False)

        if not net:
            self.warn("does not exist")
            return

        self._stop_network(net)


    def destroy(self):
        net = self.get_network(self.name, raise_exception=False)

        if not net:
            self.warn("does not exist")
            return

        if net.isActive():
            self._stop_network(net)

        self.childs_run("destroy")

        net.undefine()
        self.success("removed!")

    def suspend(self):
        pass

    def resume(self):
        pass

    def _spawn_network(self):
        self.childs_run("spawn")

        replace = {'config': "\n".join(self.xml_net),
                   'name': self.name}

        tpl = paths.template('network-component.xml')
        xml = tpl.safe_substitute(replace)

        # FIXME: Handle case where the network already is used by another
        # device
        try:
            self.virt().networkDefineXML(xml)
            net = self.get_network(self.name)
            return net
        except libvirt.libvirtError as err:
            raise error.ExecError("Could not define {}: {}".format(self.name, err))

    def _stop_network(self, net):
        self.childs_run("stop")

        if not net.isActive():
            self.say("is already stopped")
            return

        net.destroy()

        if not util.wait_until_inactive(net):
            self.warn("could not stop network")
            return
        self.say("stopped!")
        return


NetworkComponent.register()
