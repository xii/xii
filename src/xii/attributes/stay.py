
from xii import attribute, paths
from xii.attribute import Key
from xii.output import show_setting


class StayAttribute(attribute.Attribute):
    allowed_components = "network"
    defaults = False

    keys = Key.Bool

    def info(self):
        if self.settings:
            show_setting("stay when stopped", "yes")

    def does_stay(self):
        return self.settings


attribute.Register.register("stay", StayAttribute)
