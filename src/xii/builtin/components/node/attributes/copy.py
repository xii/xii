import os
import tarfile
import md5

from xii import error, util, need
from xii.validator import Dict, String, Required, Key, VariableKeys

from base import NodeAttribute


class CopyAttribute(NodeAttribute, need.NeedGuestFS):
    atype = "copy"
    requires = ["image"]

    keys = Dict([
        VariableKeys(String())
    ])

    def spawn(self):
        for dest, source in self.settings.items():

            if not os.path.isabs(dest):
                self.warn("destination path `{}` needs to be absolute"
                          .format(dest))
                continue

            if not os.path.isabs(source):
                source = os.path.join(os.getcwd(), source)

            if not os.path.exists(source):
                self.warn("source path `{}` does not exist".format(source))
                continue

            self.say("{} => {}".format(source, dest))
            if os.path.isdir(source):

                tmp = util.make_temp_name(source + dest)
                with tarfile.open(tmp, "a") as tar:
                    tar.add(source, arcname=os.path.basename(dest))
                self.guest().tar_in(tmp, os.path.split(dest)[0])
            else:
                with open(source, "r") as src:
                    self.guest().write(dest, src.read())


CopyAttribute.register()
