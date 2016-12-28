from xii.attribute import Attribute
from xii.validator import Bool


class StayAttribute(Attribute):
    atype = "stay"

    defaults = False

    keys = Bool()

    def does_stay(self):
        return self.settings
