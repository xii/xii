import libvirt

from xii import error, util
from xii.component import Component
from xii.need import NeedLibvirt, NeedIO

DEFAULT_PATH = "/etc/libvirt/hooks/qemu"
FORWARD_HOOK = "forward-hook.py"

class ForwardComponent(Component, NeedLibvirt, NeedIO):
    """Define forwards like portforwarding
    TODO: docu!
    """
    short_description="Define forwardings from instance to host"

    ctype = "forward"
    required_attributes = []
    default_attributes = []
    requires = []

    def hook_path(self):
        return self.config("hooks/port_forward_path", DEFAULT_PATH)

    def hook_exists(self):
        return self.io().exists(self.hook_path())

    def install_hook(self):
        # TODO: Implement me
        pass

    def forwards_for(self, instance):
        forwards = self.each_attribute(
            "forwards_for",
            args={"instance": instance})
        return "\n".join(util.flatten(forwards))

    def spawn(self):
        pass
        # if (not self.hook_exists() or
        #     not self._hook_check_sha(self.hook_path(), FORWARD_HOOK)):
        #     self.install_hook()
        #     self.restart_libvirtd()

    def _hook_check_sha(self, path, template_name):
        p_hash = hashlib.sha256()
        t_hash = hashlib.sha256()

        p = p_hash.update(util.file_read(path))
        t = t_hash.update(self.template(template_name))

        return p == t
