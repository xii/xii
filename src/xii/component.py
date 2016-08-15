from xii.entity import Entity, EntityRegister


class Component(Entity):
    entity = "component"
    toplevel = True
    defaults = []

    @classmethod
    def register(cls):
        EntityRegister.register_component(cls)

    def __init__(self, name, runtime):
        Entity.__init__(self, name, runtime, parent=None)

    def load_defaults(self):
        for default in self.defaults:
            attr = EntityRegister.get_entity(default, "attribute", self.entity)
            if attr.has_defaults():
                self.add(attr(attr.defaults, self))

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()
