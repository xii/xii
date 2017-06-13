from xii import error
from xii.validator import ByteSize
from xii.components.node import NodeAttribute
import re


class MemoryAttribute(NodeAttribute):
    atype = "memory"
    requires = []
    defaults = "512M"
    keys = ByteSize("512M")

    factors = {
        "k": 1,
        "M": 2,
        "G": 3,
        "T": 4
    }
    warn_on = 512 * 1024 * 1024

    def validate(self):
        NodeAttribute.validate(self)
        value, unit = self.extract(self.settings())
        in_bytes = int(value) * pow(1024, self.factors[unit])

        if unit not in self.factors.keys():
            raise error.DefError("Invalid memory size (kMGT can be used)")

        if in_bytes < self.warn_on:
            self.warn("It looks like you are trying to start a node with less "
                      "than 512M. Starting the virtual maschine's OS might not "
                      "work as expected. Raise memory in case.")

    def spawn(self):
        memory_settings = self.settings()
        value, unit = self.extract(memory_settings)
        self.verbose("setting Memory to {} {}...".format(value, unit))

        # FIXME: Move to a template
        memory = "<memory unit='{}'>{}</memory>".format(unit, value)
        current_memory = ("<currentMemory unit='{}'>{}</currentMemory>"
                          .format(unit, value))
        memory_section = "{}\n{}".format(memory, current_memory)
        self.add_xml("core", memory_section)

    def extract(self, memory):
        validator = re.compile("(?P<value>\d+)(\ *)(?P<unit>[GkMT])")
        result = validator.search(memory)
        return (result.group("value"), result.group("unit"))
