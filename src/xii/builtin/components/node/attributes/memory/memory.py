from xii.validator import ByteSize
from xii.components.node import NodeAttribute
import re


class MemoryAttribute(NodeAttribute):
    atype = "memory"
    requires = []
    defaults = "128M"

    keys = ByteSize("128M")

    def spawn(self):
        memory_settings = self.settings()
        value, unit = self.extract(memory_settings)
        self.verbose("setting Memory to {} {}...".format(value, unit))
        memory = "<memory unit='{}'>{}</memory>".format(unit, value)
        current_memory = "<currentMemory unit='{}'>{}</currentMemory>".format(unit, value)
        memory_section = "{}\n{}".format(memory, current_memory)
        self.add_xml("core", memory_section)

    def extract(self, memory):
        validator = re.compile("(?P<value>\d+)(\ *)(?P<unit>[GkMT])")
        result = validator.search(memory)
        return (result.group("value"), result.group("unit"))
