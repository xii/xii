from xii.entity import EntityRegister, Entity
from xii.store import HasStore

class Attribute(Entity, HasStore):
    attribute=""
    defaults = None
    keys = None

    @classmethod
    def has_defaults(cls):
        if cls.defaults is None:
            return False
        return True

    @classmethod
    def default(cls, cmpnt):
        return cls(cls.defaults, cmpnt)

    def __init__(self, component):
        Entity.__init__(self, name=self.attribute,
                              parent=component)

    def store(self):
        return self.parent().store().get(self.attribute)

    def component_entity(self):
        return self.parent().entity()

    def other_attribute(self, name):
        return self.parent().get_attribute(name)

    def validate(self):
        self.keys.validate(self.component_entity() + " > " + self.entity(), self.store().values())

    def get_virt_url(self):
        return self.connection("connection", "FAILING")
