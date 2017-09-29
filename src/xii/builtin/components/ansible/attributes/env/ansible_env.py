
from xii.components.ansible import AnsibleAttribute
from xii.validator import String, VariableKeys, Dict


class EnvAttribute(AnsibleAttribute):
    atype = "env"
    keys = Dict([VariableKeys(String("some value"), example="name")])
    defaults = {}

    def get_vars(self):
        return self.settings()

