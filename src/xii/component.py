from xii.entity import Entity
from xii.store import HasStore
from xii import error


class Component(Entity, HasStore):
    ctype = ""
    default_attributes = []
    required_attributes = []

    def __init__(self, name, command, tpls={}):
        Entity.__init__(self, name, parent=command, templates=tpls)

    def get_virt_url(self):
        return self.get("settings/connection", "qemu://system")

    # limit access to component/type/concret_instance
    def store(self):
        path = "components/{}/{}".format(self.ctype, self.entity())
        return self.parent().store().derive(path)

    def attributes(self):
        return self._childs

    def add_attribute(self, attribute):
        return self.add_child(attribute)

    def each_attribute(self, action, reverse=False):
        return self.each_child(action, reverse)

    def get_attribute(self, name):
        return self.get_child(name)

    def has_attribute(self, name):
        return not self.get_child(name) is None

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def validate(self):
        Entity.validate(self, self.required_attributes)


def from_definition(definition, command, ext_mgr):
    for component_type in definition:
        for name in definition[component_type].keys():
            cmpnt = ext_mgr.get_component(component_type)

            if not cmpnt:
                raise error.NotFound("Could not find component type {}!"
                                     .format(component_type))
            instance = cmpnt["class"](name, command, cmpnt["templates"])
            _initialize_attributes(instance, ext_mgr)

            yield instance


def _initialize_attributes(instance, ext_mgr):
    non_attributes = ["count", "type", "settings"]

    def add_attr(name):
        attr = ext_mgr.get_attribute(instance.ctype, name)

        if not attr:
            raise error.NotFound("Invalid attribute `{}` for component "
                                 "{}. Maybe Missspelled?"
                                 .format(name, instance.entity()))

        instance.add_attribute(attr["class"](instance, attr["templates"]))

    # load defined attributes
    for n in instance.store().values().keys():
        if n not in non_attributes:
            add_attr(n)

    # add defaults
    for name in instance.default_attributes:
        if not instance.has_attribute(name):
            add_attr(name)

    # check if all required attributes are set
    for name in instance.required_attributes:
        if not instance.has_attribute(name):
            raise error.NotFound("{} needs a {} attribute but not found, "
                                 "add one!".format(instance.ctype, name))
