from xii import error
from xii.attribute import Attribute
from xii.validator import Bool
from xii.output import info, show_setting, warn


class HostnameAttribute(Attribute):
    attr_name = "hostname"
    allowed_components = "node"
    requires = ["image"]
    defaults = True

    keys = Bool()

    def prepare(self):
        if not self.settings:
            return
        self.add_info("set hostname", "yes")

    def spawn(self):
        if not self.settings:
            return


        name = self.name
        guest = self.conn().guest(self.cmpnt.attribute('image').image_path())

        for replace in ["#", "."]:
            name = name.replace(replace, "-")

        self.say("setting hostname to {}...".format(name))
        guest.write('/etc/hostname', name)


HostnameAttribute.register()
