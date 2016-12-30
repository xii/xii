from xii.validator import Bool
from xii.components.pool import PoolAttribute


class PersistentAttribute(PoolAttribute):
    atype = "persistent"
    keys = Bool()
    defaults = True

    def is_persistent(self):
        return self.settings()
