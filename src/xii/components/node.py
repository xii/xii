import libvirt

from xii import component, paths, util, error
from xii.output import info, warn


class NodeComponent(component.Component):
    require_properties = ['image']

    libvirt_xml = []

    def add_xml(self, xml):
        self.libvirt_xml.append(xml)

    def prepare(self):
        self.count = self.attribute('count')

    def start(self):
        self.prepare()

        domains = self.attribute('count').counted_names()

        for domain_name in domains:
            domain = util.libvirt_get_domain(self.virt(), domain_name)

            if not domain:
                info("Creating node {}...".format(domain_name))

                xml = paths.template('node.xml')
                replacements = {'name': domain_name}

                try:
                    self.virt().defineXML(xml.safe_substitute(replacements))
                    domain = util.libvirt_get_domain(self.virt(), domain_name)
                except libvirt.libvirtError as err:
                    raise error.LibvirtError(err, "Could not start "
                                                  "domain {}".format(domain_name))

            if domain.isActive():
                warn("{} is already active. Skipping.".format(domain_name))
                continue

            info("Starting {}...".format(domain_name))
            domain.create()

component.Register.register('node', NodeComponent)
