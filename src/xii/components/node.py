import time

import libvirt

from xii import component, paths, util, error
from xii.output import info, warn, fatal


class NodeComponent(component.Component):
    require_attributes = ['image']
    default_attributes = ['network', 'count']

    xml_dfn = {}

    def add_xml(self, section, xml):
        self.xml_dfn[section] += "\n" + xml

    def stop(self):
        domains = self.attribute('count').counted_names()

        for domain_name in domains:
            domain = self.conn.get_domain(domain_name)

            if not domain:
                warn("{} does not exist. Can not stop "
                     "nothing".format(domain_name))
                continue

            if not domain.isActive():
                info("{} is already stopped. Nothing "
                     "todo".format(domain_name))
                continue
            
            domain.shutdown()

            for i in range(5):
                if not domain.isActive():
                    info("{} stopped".format(domain_name))
                    break
                time.sleep(1)

            if domain.isActive():
                fatal("Could not stop {}".format(domain_name))

    def start(self):
        domains = self.attribute('count').counted_names()

        caps = self.conn.get_capabilities()

        for domain_name in domains:
            self.xml_dfn = {'devices': ''}
            self.attribute_action('start', domain_name)

            domain = self.conn.get_domain(domain_name)
            if not domain:
                info("Creating node {}...".format(domain_name))

                xml = paths.template('node.xml')
                self.xml_dfn['name'] = domain_name
                self.xml_dfn.update(caps)

                try:
                    self.virt().defineXML(xml.safe_substitute(self.xml_dfn))
                    domain = self.conn.get_domain(domain_name)
                except libvirt.libvirtError as err:
                    raise error.LibvirtError(err, "Could not start "
                                                  "domain {}".format(domain_name))

            if domain.isActive():
                warn("{} is already active. Skipping.".format(domain_name))
                continue

            info("Starting {}...".format(domain_name))
            domain.create()

component.Register.register('node', NodeComponent)
