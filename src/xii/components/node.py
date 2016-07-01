import time

import libvirt

from xii import component, paths, error, domain
from xii.output import info, warn, fatal


class NodeComponent(component.Component):
    require_attributes = ['image']
    default_attributes = ['network', 'count']

    xml_dfn = {}

    def add_xml(self, section, xml):
        self.xml_dfn[section] += "\n" + xml


    def start(self):
        domains = self.attribute('count').counted_names()

        for domain_name in domains:
            domain = self.conn().get_domain(domain_name)

            if not domain:
                domain = self._spawn_domain(domain_name)

            if domain.isActive():
                warn("{} is already active. Skipping.".format(domain_name))
                continue

            self.attribute_action('start', domain_name)
            info("Starting {}...".format(domain_name))
            domain.create()
            import pdb; pdb.set_trace()

    def stop(self):
        domains = self.attribute('count').counted_names()

        for (name, dmn) in domain.each(self.conn(), domains):
            self.attribute_action('stop', name)

            if not dmn.isActive():
                info("{} is already stopped".format(name))
                continue

            dmn.shutdown()

            if not domain.wait_active(dmn, False):
                fatal("Could not stop {}".format(name))
                continue

            info("{} stopped".format(name))

    def destroy(self):
        domains = self.attribute('count').counted_names()

        for (name, dmn) in domain.each(self.conn(), domains):
            if domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
                dmn.resume()

            if domain.has_state(dmn, libvirt.VIR_DOMAIN_RUNNING):
                info("{} is running. Stopping...".format(name))
                dmn.shutdown()
                domain.wait_active(dmn, False)

            if dmn.isActive():
                fatal("Could not remove running domain {}.".format(name))
                continue

            self.attribute_action('destroy', name)
            dmn.undefine()
            info("{} removed".format(name))

    def suspend(self):
        domains = self.attribute('count').counted_names()

        for (name, dmn) in domain.each(self.conn(), domains):
            if domain.has_state(dmn, libvirt.VIR_DOMAIN_PAUSED):
                info("{} is already suspended".format(name))
                continue

            dmn.suspend()

            if not domain.wait_until(dmn, libvirt.VIR_DOMAIN_PAUSED):
                fatal("Could not suspend {}".format(name))
                continue

            info("{} suspended".format(name))

    def resume(self):
        domains = self.attribute('count').counted_names()

        for (name, d) in domain.each(self.conn(), domains):

            if domain.has_state(d, libvirt.VIR_DOMAIN_RUNNING):
                info("{} is already running".format(name))
                continue

            if not domain.has_state(d, libvirt.VIR_DOMAIN_PAUSED):
                info("{} is not suspended".format(name))
                continue

            d.resume()

            if not domain.wait_until(d, libvirt.VIR_DOMAIN_RUNNING):
                fatal("Could not resume {}".format(name))
                continue

            info("{} resumed".format(name))

    def _spawn_domain(self, domain_name):
        self.xml_dfn = {'devices': ''}
        self.attribute_action('spawn', domain_name)

        caps = self.conn().get_capabilities()

        info("Creating node {}...".format(domain_name))

        xml = paths.template('node.xml')
        self.xml_dfn['name'] = domain_name
        self.xml_dfn.update(caps)

        try:
            self.virt().defineXML(xml.safe_substitute(self.xml_dfn))
            domain = self.conn().get_domain(domain_name)
            return domain
        except libvirt.libvirtError as err:
            raise error.LibvirtError(err, "Could not start "
                    "domain {}".format(domain_name))


component.Register.register('node', NodeComponent)
