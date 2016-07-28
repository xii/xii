from xii import error, guest_util
from xii.attribute import Attribute
from xii.validator import Bool
from xii.output import info, show_setting, warn


class HostnameAttribute(Attribute):
    attr_name = "hostname"
    allowed_components = "node"
    requires = ["image"]
    defaults = True

    keys = Bool()

    def info(self):
        if self.settings:
            show_setting("set hostname", "yes")

    def spawn(self):
        name = self.name

        info("Setting hostname")
        guest = self.conn().guest(self.cmpnt.attribute('image').image_path())

        for replace in ["#", "."]:
            name = name.replace(replace, "-")

        guest.write('/etc/hostname', name)


HostnameAttribute.register()
