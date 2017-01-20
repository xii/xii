from xii.validator import Bool
from xii.components.pool import PoolAttribute


class PersistentAttribute(PoolAttribute):
    atype = "persistent"
    keys = Bool("False")
    defaults = True

    def is_persistent(self):
        return self.settings()
