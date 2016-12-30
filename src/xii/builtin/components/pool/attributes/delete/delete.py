from xii.validator import Bool
from xii.components.pool import PoolAttribute


class DeleteAttribute(PoolAttribute):
    atype = "delete"
    keys = Bool()
    defaults = True

    def delete(self):
        return self.settings()
