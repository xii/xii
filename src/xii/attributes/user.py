import os
import subprocess
import stat

from urllib2 import urlparse

from xii import attribute, paths, error
from xii.output import info, show_setting


class UserAttribute(attribute.Attribute):
    name = "user"
    allowed_components = "node"

    def spawn(self, domain_name):
        guest = self.conn().guest(self.cmpnt.attribute('image').clone(domain_name))

attribute.Register.register("user", UserAttribute)
