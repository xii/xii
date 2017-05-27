
from xii.component import Component
from xii.need import NeedIO, NeedSSH
from xii import error

from ansible import NeedAnsible


class AnsibleComponent(Component, NeedAnsible, NeedIO, NeedSSH):
    """
    Easily provision created images using standard ansible.

    .. note::
        Make sure the ansible commandline tool is installed and working
        if you want to use this feature.

    Example definition:
    ::

      # vim: set ts=2 sw=2 tw=0 ft=yaml:
      ---
      my-vms:
        type: node
        pool: default
        image: {{ image }}
        count: 4
        user:
          root:
            password: linux
        ssh:
            copy-key:
              users:
                - root
      privision-vms:
        type: ansible
        hosts:
          all: my-vms
          group-A: [my-vms-1, my-vms-3]
          group-B: [my-vms-2, my-vms-4]
        run: privison-vms.yml
        env:
          extra_env: additional_variables.conf

    Checkout the :doc:`/components/ansible/hosts` for more information about
    how to populate the inventor list
    """
    short_description="Provision virtual hosts using ansible"

    ctype = "ansible"
    required_attributes = ["hosts", "run"]
    default_attributes = ["hosts", "env"]

    requires = ["network", "node"]

    def fetch_metadata(self):
        # no metadata here
        return None

    def status(self):
        # FIXME: Find a way to get status if ansible has run or not
        return "UNKNOWN"

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
