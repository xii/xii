from xii import error
from xii.attributes.base import NodeAttribute
from xii.validator import Bool
from xii.need import NeedGuestFS


class HostnameAttribute(NodeAttribute, NeedGuestFS):
    entity = "hostname"

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
