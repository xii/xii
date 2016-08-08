from xii.attribute import Attribute
from xii.validator import Bool
from xii.output import show_setting


class StayAttribute(Attribute):
    entity = "stay"
    needs = ["network"]

    defaults = False

    keys = Bool()

    def info(self):
        if self.settings:
            show_setting("stay when stopped", "yes")

    def does_stay(self):
        return self.settings


StayAttribute.register()
