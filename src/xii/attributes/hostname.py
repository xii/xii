from xii import attribute, error, guest_util
from xii.attribute import Key
from xii.output import info, show_setting, warn


class HostnameAttribute(attribute.Attribute):
    name = "hostname"
    allowed_components = "node"
    requires = ["image"]
    defaults = True

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


attribute.Register.register('hostname', HostnameAttribute)
