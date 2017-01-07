from xii import error, need
from xii.validator import Bool

from xii.components.node import NodeAttribute


class HostnameAttribute(NodeAttribute, need.NeedGuestFS):
    atype = "hostname"
    requires = ["image"]
    defaults = True

    keys = Bool(True)

    def spawn(self):
        if not self.settings():
            return

        name = self.component_entity()

        for replace in ["#", "."]:
            name = name.replace(replace, "-")

        self.say("setting hostname to {}...".format(name))
        self.guest().write('/etc/hostname', name)
