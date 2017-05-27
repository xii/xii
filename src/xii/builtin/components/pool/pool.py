import libvirt
from time import time

from xii.component import Component
from xii.need import NeedLibvirt, NeedIO
from xii import error


class PoolComponent(Component, NeedLibvirt, NeedIO):
    ctype = "pool"

    xml_pool = []

    default_attributes = ["persistent", "delete"]
    required_attributes = ["persistent", "delete"]

    def validate(self):
        type_spec = len(filter(lambda a: a.pool_type, self.attributes()))
        if type_spec != 1:
            raise error.ValidatorError("{} component must have exactly one "
                                       "attribute specifing its type (has {} "
                                       "needs 1)"
                                       .format(self.entity(), type_spec))
        return Component.validate(self)

    def add_xml(self, xml):
        self.xml_pool.append(xml)

    def fetch_metadata(self):
        return self.fetch_resource_metadata("pool", self.entity())

    def status(self):
        domain = self.get_pool(self.entity(), raise_exception=False)
        if domain is None:
            return colors.WARN + "NOT CREATED" + colors.CLEAR
        if domain.isActive():
            return colors.SUCCESS + "RUNNING" + colors.CLEAR
        return "STOPPED/SUSPENDED"

    def spawn(self):
        self.say("spawning...")
        self.xml_pool = []
        self.each_attribute("spawn")

        self.add_meta({
            "created" : time(),
            "definition": self.config("runtime/definition"),
            "user": self.io().user()
            })

        pool_tpl = self.template("pool.xml")
        xml = pool_tpl.safe_substitute({
            "type": self.attributes()[0].pool_type,
            "name": self.entity(),
            "config": "\n".join(self.xml_pool),
            "meta": self.meta_to_xml()
        })

        self.finalize()
        try:
            if self.get_attribute("persistent").is_persistent():
                self.virt().storagePoolDefineXML(xml)
            else:
                self.warn("is beging created as non-persistent pool storage")
                self.virt().storagePoolCreateXML(xml)
            pool = self.get_pool(self.entity())
            self.each_attribute("after_spawn")
            return pool
        except libvirt.libvirtError as err:
            raise error.ExecError("Could create pool {}: {}".format(self.entity(), err))

    def start(self):
        self.say("starting...")
        pool = self.get_pool(self.entity())

        self.each_attribute("start")
        if not pool.isActive():
            pool.create()
        self.each_attribute("after_start")

        # cleanup environment
        self.finalize()
        self.success("started!")

    def stop(self):
        self.say("stopping...")
        pool = self.get_pool(self.entity())

        self.each_attribute("stop", reverse=True)
        pool.destroy()
        self.each_attribute("after_stop", reverse=True)
        self.success("stopped!")

    def destroy(self):
        self.say("destroying...")
        pool = self.get_pool(self.entity(), raise_exception=False)

        if not pool:
            self.say("pool {} does not exist or was already destroyed"
                     .format(self.entity()))
            return

        if pool.isActive():
            self.stop()

        if self.get_attribute("delete").delete():
            self.warn("deleting content from pool...")
            pool.delete()

        self.each_attribute("destroy", reverse=True)
        pool.undefine()
        self.success("destroyed!")
