import libvirt
from time import sleep, time

from xii import error
from xii.component import Component
from xii.need import NeedLibvirt, NeedIO
from xii.util import domain_has_state, domain_wait_state, wait_until_inactive


class NodeComponent(Component, NeedLibvirt, NeedIO):
    """Define, create, manage virtual machines

    das ja mehr als strange
    """
    short_description="Define and manage virtual machines"

    ctype = "node"
    required_attributes = ["pool", "image"]
    default_attributes = ["pool", "network", "hostname"]

    requires = ["pool", "network"]

    xml_dfn = {'devices': ""}
    xml_metadata = {}

    def __init__(self, name, command, tpls):
        Component.__init__(self, name, command, tpls)
        self._temp_dir = None

    def add_xml(self, section, xml):
        self.xml_dfn[section] += "\n" + xml

    def add_meta(self, key, value):
        self.xml_metadata[key] = value

    # every node has an image
    def get_domain_image_path(self):
        return self.get_attribute('image').get_domain_image_path()

    def create(self):
        domain = self.get_domain(self.entity(), raise_exception=False)
        if domain is not None:
            return

        self.io().ensure_path_exists(self.get_temp_path())

        self.say("creating...")
        self.each_attribute("create")

    def spawn(self):
        domain = self.get_domain(self.entity(), raise_exception=False)
        if domain is not None:
            return

        self.say("spawning...")
        self.xml_dfn = {'devices': ''}
        self.each_attribute("spawn")

        caps = self.get_capabilities()
        self.add_meta('created', time())
        self.add_meta('definition', self.config("runtime/definition"))
        self.add_meta('user', self.io().user())

        xml = self.template('node.xml')
        self.xml_dfn['name'] = self.entity()
        self.xml_dfn['meta'] = self._generate_meta_xml()
        self.xml_dfn.update(caps)

        try:
            self.virt().defineXML(xml.safe_substitute(self.xml_dfn))
        except libvirt.libvirtError as err:
            raise error.ExecError("Could not start {}: {}".format(self.entity(), str(err)))
        self.each_attribute("after_spawn")


    def start(self):
        domain = self.get_domain(self.entity())

        if domain.isActive():
            self.say("is already started")
            return

        self.say("starting ...")
        self.each_attribute("start")
        domain.create()

        self.success("started!")
        self.each_child("after_start")

        # remove template path
        self.io().rm(self.get_temp_path())


    def stop(self, force=False):
        domain = self.get_domain(self.entity())

        self.each_child("stop", reverse=True)
        self._stop_domain(domain, force)
        self.each_child("after_stop", reverse=True)

    def destroy(self):
        self.say("destroying...")
        domain = self.get_domain(self.entity(), raise_exception=False)

        if not domain:
            self.warn("does not exist")
            return

        if domain_has_state(domain, libvirt.VIR_DOMAIN_PAUSED):
            domain.resume()

        if domain_has_state(domain, libvirt.VIR_DOMAIN_RUNNING):
            self._stop_domain(domain, force=True)

        if domain.isActive():
            raise error.Bug("Could not remove running "
                            "domain {}".format(self.ident()))

        self.each_child("destroy", reverse=True)
        domain.undefine()
        self.success("removed!")
        self.each_child("after_destroy", reverse=True)

    def suspend(self):
        self.say("suspending...")
        domain = self.get_domain(self.entity(), raise_exception=False)

        if not domain:
            self.warn("does not exist")
            return

        if domain_has_state(domain, libvirt.VIR_DOMAIN_PAUSED):
            self.warn("is already suspended")
            return

        self.each_child("suspend")
        domain.suspend()

        if not domain_wait_state(domain, libvirt.VIR_DOMAIN_PAUSED):
            self.warn("failed to suspend")
            return
        self.success("suspended!")

    def resume(self):
        self.say("resuming...")
        domain = self.get_domain(self.entity(), raise_exception=False)

        if not domain:
            self.warn("does not exist")
            return

        if domain_has_state(domain, libvirt.VIR_DOMAIN_RUNNING):
            self.say("is already running")
            return

        if not domain_has_state(domain, libvirt.VIR_DOMAIN_PAUSED):
            self.say("is not suspended")
            return

        self.each_child("resume")
        domain.resume()

        if not domain_wait_state(domain, libvirt.VIR_DOMAIN_RUNNING):
            self.warn("could not resumed")
            return

        self.success("resumed!")
        self.each_child("after_resume")

    def _stop_domain(self, domain, force=False):
        if not domain.isActive():
            self.say("is already stopped")
            return

        if domain_has_state(domain, libvirt.VIR_DOMAIN_PAUSED):
            domain.resume()

        domain.shutdown()

        if not wait_until_inactive(domain):
            # Try to force off
            domain.destroy()
            if not wait_until_inactive(domain):
                self.warn("could not be stopped")
                return
        self.success("stopped!")

    def _generate_meta_xml(self):
        meta = "<xii:node xmlns:xii=\"http://xii-project.org/xmlns/node/1.0\">\n"
        for k, v in self.xml_metadata.items():
            meta += "<xii:{key}>{value}</xii:{key}>\n".format(key=k, value=v)
        meta += "</xii:node>\n"
        return meta
