
import xml.etree.ElementTree as etree

from xii import error, need
from xii.attribute import Attribute
from xii.validator import String


class PoolAttribute(Attribute, need.NeedLibvirt):
    atype = "pool"
    keys = String()
    defaults = "default"

    def after_spawn(self):
        pool = self.used_pool()

        if not pool.isActive():
            pool.create()

    def used_pool(self):
        pool = self.get_pool(self.settings(), raise_exception=False)

        if not pool:
            if not self.has_component("pool", self.settings()):
                raise error.NotFound("pool {} does not exist.")

            for i in range(self.global_get("global/retry_pool", 20)):
                pool = self.get_pool(name, raise_exception=False)
                if pool:
                    break
                self.counted(i, "Waiting for pool {} to become ready."
                             .format(self.settings()))
                sleep(self.global_get("global/wait", 3))

            raise error.ExecError("Coult not start pool {}!"
                                .format(self.settings()))
        return pool

    def used_pool_name(self):
        return self.settings()

    def used_pool_type(self):
        pool = self.used_pool()
        xml = etree.fromstring(pool.XMLDesc())
        return xml.attrib["type"]
