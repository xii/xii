import os
import subprocess
import stat

import xml.etree.ElementTree as etree

from xii import paths, error, need
from xii.attribute import Attribute
from xii.validator import String
from xii.entity import EntityRegister

class PoolAttribute(Attribute, need.NeedIO, need.NeedLibvirt):
    atype = "pool"

    keys = String()

    defaults = 'xii'

    def get_used_pool(self):
        pool = self.get_pool(self.settings, raise_exception=False)

        if not pool:
            # support the default volume pool
            if self.settings == "xii":
                return self._initialize_default_pool()

            # check if pool is defined and wait for its creation
            has_definition = self.get_definition().item(self.settings,
                                                        item_type="pool")
            if not has_definition:
                raise error.NotFound("Could not find pool {}"
                                     .format(self.settings))

            for i in range(self.get_config().retry("pool")):
                self.counted(i, "Waiting for pool {} to become ready"
                                .format(self.settings))

                pool = self.get_pool(self.settings, raise_exception=False)

                if pool:
                    return pool
                sleep(self.get_config().wait())
            raise error.ExecError("Pool {} has not become ready "
                                  "in time".format(self.settings))
        return pool

    def get_used_pool_type(self):
        pool = self.get_used_pool()

        xml = etree.fromstring(pool.XMLDesc())

        return xml.attrib["type"]

    def get_used_pool_name(self):
        return self.settings

    def _default_pool_path(self):
        home = self.io().user_home()
        return paths.xii_home(home, 'pool')

    def _initialize_default_pool(self):
        path = self._default_pool_path()
        user = self.io().user()
        groups = self.io().get_groups()
        users = self.io().get_users()

        # check if directory exists
        if not self.io().exists(path):
            self.io().mkdir(path, recursive=True)

        # Changed rights
        self.io().chmod(path, stat.S_IXOTH, append=True)
        self.io().chown(path, users[user]["uid"], groups["qemu"]["gid"])

        # again
        cmd = ["setfacl", "--modify", "user:{}:x".format(user), path]
        setfacl = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        setfacl.communicate()

        if setfacl.returncode != 0:
            raise error.ExecError("Could not create default storage: Permission denied")

        # define the pool
        xii_pool_tpl = paths.template('xii_default_pool.xml')
        xii_pool = xii_pool_tpl.safe_substitute({'storage': path})

        pool = self.virt().storagePoolDefineXML(xii_pool)
        pool.setAutostart(True)

        return pool

    def spawn(self):
        pool = self.get_used_pool()
        if not pool.isActive():
          pool.create()

EntityRegister.register_attribute("node", PoolAttribute)
