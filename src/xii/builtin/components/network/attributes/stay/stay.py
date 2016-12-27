from xii.validator import Bool

from base import NetworkAttribute


class StayAttribute(NetworkAttribute):
    atype = "stay"

    defaults = False

    keys = Bool()

    def does_stay(self):
        return self.settings
