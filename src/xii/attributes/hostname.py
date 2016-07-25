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

    def spawn(self, domain_name):

        info("Setting hostname")
        guest = self.conn().guest(self.cmpnt.attribute('image').clone(domain_name))

        for replace in ["#", "."]:
            domain_name = domain_name.replace(replace, "-")

        guest.write('/etc/hostname', domain_name)


attribute.Register.register('hostname', HostnameAttribute)
