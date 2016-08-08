import libvirt

from xii.component import Component
from xii import error, paths, util
from xii.output import info, fatal


class NetworkComponent(Component):
    entity = "network"

    defaults = ['stay']
    requires = ['mode']

    xml_net = []

    def add_xml(self, xml):
        self.xml_net.append(xml)

    def start(self):
        net = self.conn().get_network(self.name, raise_exception=False)

        if not net:
            net = self._spawn_network()

        if net.isActive():
            info("{} is already started".format(self.name))
            return True

        net.create()

        if not util.wait_until_active(net):
            fatal("Could not start network {}".format(self.name))
            return False


    def stop(self):
        net = self.conn().get_network(self.name)
        self._stop_network(net)


    def destroy(self):
        net = self.conn().get_network(self.name)

        if net.isActive():
            self._stop_network(net)

        net.undefine()
        info("{} removed".format(self.name))

    def suspend(self):
        pass

    def resume(self):
        pass

    def _spawn_network(self):
        self.attribute_action('spawn')
        replace = {'config': "\n".join(self.xml_net),
                   'name': self.name}

        tpl = paths.template('network-component.xml')
        xml = tpl.safe_substitute(replace)

        # FIXME: Handle case where the network already is used by another
        # device
        try:
            self.virt().networkDefineXML(xml)
            net = self.conn().get_network(self.name)
            return net
        except libvirt.libvirtError as err:
            raise error.ExecError("Could not define {}: {}".format(self.name, err))

    def _stop_network(self, net):
        self.attribute_action('stop')

        if not net.isActive():
            info("{} is already stopped".format(self.name))
            return

        net.destroy()

        if not util.wait_until_inactive(net):
            fatal("Could not stop {}".format(self.name))
            return
        info("{} stopped".format(self.name))
        return


NetworkComponent.register()
