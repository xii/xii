from xii.validator import Bool
from xii.components.network import NetworkAttribute


class StayAttribute(NetworkAttribute):
    atype = "stay"

    defaults = False

    keys = Bool(example=True)

    def does_stay(self):
        return self.settings()
