import time

import libvirt

from xii import component, paths, error, domain
from xii.output import info, warn, fatal, section


class NodeComponent(component.Component):
    require_attributes = ['image']
    default_attributes = ['network', 'hostname']

    xml_dfn = {}

    def add_xml(self, section, xml):
        self.xml_dfn[section] += "\n" + xml

    def start(self):
        dmn = self.conn().get_domain(self.name, raise_execption=False)

        if not dmn:
            dmn = self._spawn_domain()

        if dmn.isActive():
            warn("{} is already active. Skipping.".format(self.name))
            return

        self.attribute_action('start')
        section("Starting {}".format(self.name))
        dmn.create()

    def stop(self, force=False):
        dmn = self.conn().get_domain(self.name)

        self.attribute_action('stop')
        self._stop_domain(dmn, force)

    def destroy(self):
        section("Destroying {}".format(self.name))
        dmn = self.conn().get_domain(self.name)

        if domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
            dmn.resume()

        if domain.has_state(dmn, libvirt.VIR_DOMAIN_RUNNING):
            self._stop_domain(dmn, force=True)

        if dmn.isActive():
            fatal("Could not remove running domain {}.".format(self.name))
            return

        self.attribute_action('destroy')
        dmn.undefine()
        info("{} removed".format(self.name))

    def suspend(self):
        section("Suspending {}".format(self.name))
        dmn = self.conn().get_domain(self.name)

        if domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
            info("{} is already suspended".format(self.name))
            return

        dmn.suspend()

        if not domain.wait_until(dmn, libvirt.VIR_DOMAIN_PAUSED):
            fatal("Could not suspend {}".format(self.name))
            return
        info("{} suspended".format(self.name))

    def resume(self):
        section("Resuming {}".format(self.name))
        dmn = self.conn().get_domain(self.name)

        if domain.has_state(dmn, libvirt.VIR_DOMAIN_RUNNING):
            info("{} is already running".format(self.name))
            return

        if not domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
            info("{} is not suspended".format(self.name))
            return

        dmn.resume()

        if not domain.wait_until(dmn, libvirt.VIR_DOMAIN_RUNNING):
            fatal("Could not resume {}".format(self.name))
            return

        info("{} resumed".format(self.name))

    def _spawn_domain(self):
        section("Spawning {}".format(self.name))
        self.xml_dfn = {'devices': ''}

        self.attribute_action('spawn')

        # Close open guest connection for this domain
        self.conn().close_guest(self.name)

        caps = self.conn().get_capabilities()

        xml = paths.template('node.xml')
        self.xml_dfn['name'] = self.name
        self.xml_dfn.update(caps)

        try:
            self.virt().defineXML(xml.safe_substitute(self.xml_dfn))
            dmn = self.conn().get_domain(self.name)
            return dmn
        except libvirt.libvirtError as err:
            raise error.LibvirtError(err, "Could not start "
                                          "domain {}".format(self.name))

    def _stop_domain(self, dmn, force=False):
            if not dmn.isActive():
                info("{} is already stopped".format(self.name))
                return

            if domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
                dmn.resume()

            dmn.shutdown()

            if not domain.wait_active(dmn, False):
                if not force:
                    fatal("Could not stop {}".format(self.name))
                    fatal("If you want to force shutdown. Try --force")
                    return

                # Try to force off
                dmn.destroy()
                if not domain.wait_active(dmn, False):
                    fatal("Could not stop {}".format(self.name))
                    return
            info("{} stopped".format(self.name))


component.Register.register('node', NodeComponent)
