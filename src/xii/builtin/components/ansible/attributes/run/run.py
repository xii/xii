import os

from xii import error
from xii.components.ansible import AnsibleAttribute
from xii.validator import String
from xii.need import NeedIO


class RunAttribute(AnsibleAttribute, NeedIO):
    atype = "run"
    keys = String("/path/to/playbook.yml")

    def validate(self):
        AnsibleAttribute.validate(self)

        if not os.path.exists(self.settings()):
            raise error.NotFound("Could not find ansible playbook: "
                                 "{} no such file or directory"
                                 .format(self.settings()))

    def get_playbook(self, tmp):
        playbook = os.path.join(tmp, "playbook.yml")
        self.io().copy(self.settings(), playbook)
        return playbook
