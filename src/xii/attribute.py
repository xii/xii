from xii.entity import Entity
from xii.store import HasStore, Store

class Attribute(Entity, HasStore):
    atype=""
    defaults = None
    keys = None

    @classmethod
    def has_defaults(cls):
        if cls.defaults is None:
            return False
        return True

    def __init__(self, component, tpls):
        Entity.__init__(self,
                        name=self.atype,
                        parent=component,
                        templates=tpls)

    def settings(self, key=None, default=None):
        if self.get(self.atype):
            s = self.store().derive(self.atype)
        elif self.has_defaults():
            s = Store(parent=self.defaults)

        if key is None:
            return s.values()
        return s.get(key, default)

    def share(self, name, creator, finalizer=None):
        return self.parent().share(name, creator, finalizer)

    def store(self):
        return self.parent().store()

    def component_entity(self):
        return self.parent().entity()

    def other_attribute(self, name):
        return self.parent().get_attribute(name)

    def validate(self):
        self.keys.validate(self.component_entity() + " > " + self.entity(), self.settings())

    def get_virt_url(self):
        return self.get("settings/connection", "FAILING")
