from xii import error, need
from xii.validator import Bool

from base import NodeAttribute


class HostnameAttribute(NodeAttribute, need.NeedGuestFS):
    atype = "hostname"
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

        name = self.component_name()

        for replace in ["#", "."]:
            name = name.replace(replace, "-")

        self.say("setting hostname to {}...".format(name))
        self.guest().write('/etc/hostname', name)


HostnameAttribute.register()
