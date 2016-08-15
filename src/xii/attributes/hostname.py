from xii import error
from xii.attributes.nodeattribute import NodeAttribute
from xii.validator import Bool
from xii.need import NeedGuestFS
from xii.output import info, show_setting, warn


class HostnameAttribute(NodeAttribute, NeedGuestFS):
    entity = "hostname"
    needs = "node"

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