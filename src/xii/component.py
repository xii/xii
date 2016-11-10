from xii.entity import Entity, EntityRegister
from xii.store import HasStore

non_attributes = ["count", "type", "settings"]

class Component(Entity, HasStore):
    ctype = ""
    default_attrs = []

    @classmethod
    def register(cls):
        EntityRegister.register_component(cls)

    def __init__(self, name, command):
        Entity.__init__(self, name, parent=command)

    # limit access to component/type/concret_instance
    def store(self):
        path = "components/{}/{}".format(self.ctype, self.entity())
        return self.parent().store().derive(path)

    def add_attribute(self, attribute):
        return self.add_child(attribute)

    def each_attribute(self, action, reverse=False):
        return self.each_child(action, reverse)

    def get_attribute(self, name):
        return self.get_child(name)

    def load_defaults(self): 
        for default in self.default_attributes:
            if default in self.store().values():
                continue
            attr = EntityRegister.get_attribute(self.ctype, default)
            if attr.has_defaults():
                self.add_attribute(attr(self))

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def validate(self):
        Entity.validate(self, self.required_attributes)


def from_definition(store, command):
    components = []

    definition = store.get("components")
    for component_type in definition:
        for name in definition[component_type].keys():
            components.append(_create_component(name, component_type, command))
    return components

def _create_component(name, component_type, command):

    component_class = EntityRegister.get_component(component_type)
    component = component_class(name, command)

    component.load_defaults()

    for attr_name in component.store().values().keys():        
        if attr_name in non_attributes:
            continue
        attr = EntityRegister.get_attribute(component_type, attr_name)
        if not attr:
            raise NotFound("Invalid attribute `{}` for component "
                           "{}. Maybe Missspelled?"
                           .format(attr_name, component.entity()))
        component.add_attribute(attr(component))

    # check if component is correctly initialized
    component.validate()
    return component
