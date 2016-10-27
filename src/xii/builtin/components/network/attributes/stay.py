from xii.attributes.base import NetworkAttribute
from xii.validator import Bool


class StayAttribute(NetworkAttribute):
    entity = "stay"
    needs = ["network"]

    defaults = False

    keys = Bool()

    def info(self):
        if self.settings:
            pass
            # show_setting("stay when stopped", "yes")

    def does_stay(self):
        return self.settings


StayAttribute.register()
