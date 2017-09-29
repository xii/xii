from xii.validator import Int
from xii.components.node import NodeAttribute


class CPUAttribute(NodeAttribute):
    atype = "cpu"
    requires = []
    defaults = 2

    keys = Int(2)

    def spawn(self):
        vcpu = self.settings()
        self.verbose("setting CPU count to {}...".format(vcpu))
        self.add_xml("vcpu", vcpu)
