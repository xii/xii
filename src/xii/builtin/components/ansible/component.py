
from xii.component import Component
from xii.need import NeedIO, NeedSSH
from xii import error

from ansible import NeedAnsible


class AnsibleComponent(Component, NeedAnsible, NeedIO, NeedSSH):
    ctype = "ansible"
    required_attributes = ["hosts", "run"]
    default_attributes = ["hosts", "env"]

    requires = ["network", "node"]

    def ansible_executable(self):
        return "ansible-playbook"

    def validate(self):
        if not self.is_ansible_installed():
            raise error.NotFound("Need ansible installed to provision nodes")
        Component.validate(self)

    def start(self):
        tmp = self.io().mktempdir("xii-ansible")
        inventory = self.get_attribute("hosts").generate_inventory(tmp)
        envvars = self.get_attribute("env").get_vars()
        playbook = self.get_attribute("run").get_playbook(tmp)

        try:
            self.say("run playbook...")
            # FIXME: Make sure all hosts are up now!
            status = self.run_playbook(inventory, playbook, env=envvars)
        finally:
            self.io().rm(tmp)

        if status:
            self.success("provisioned!")
        else:
            self.warn("provisioning failed!")
