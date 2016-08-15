from xii import attribute, error, util
from xii.output import debug, HasOutput
from xii.entity import Entity, EntityRegister


class Component(Entity):
    entity="component"
    toplevel=True

    defaults = []

    @classmethod
    def register(cls):
        EntityRegister.register("component", cls)

    def __init__(self, name, runtime):
        Entity.__init__(self, name, runtime, parent=None)

    def load_defaults(self):
        for default in self.defaults:
            attr = EntityRegister.get_entity("attribute", default)
            if attr.has_defaults():
                self.add(attr(attr.defaults, self))

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

# class Component(HasOutput, Managed, Register):
#     require_attributes = []
#     default_attributes = []

#     @classmethod
#     def register(cls):
#         Component.register_class(cls.name, cls)

#     def get_ident(self):
#         return [self.component_name]

#     def __init__(self, name, conn, conf):
#         self.connection = conn
#         self.attrs = []
#         self.component_name = name
#         self.conf = conf
#         self.prepare()

#     def add_attribute(self, name, attr):
#         for idx, a in enumerate(self.attrs):
#             if a.attr_name == name:
#                 self.attrs[idx] = attr
#                 return
#         self.attrs.append(attr)


#     def virt(self):
#         return self.conn().virt()

#     def conn(self):
#         return self.connection

#     def attribute(self, name):
#         for attr in self.attrs:
#             if attr.attr_name == name:
#                 return attr
#         debug("Could not find attribute {}".format(name))
#         return None

#     def add_default_attributes(self):
#         for attr_name in self.default_attributes:
#             # Assume default attributes must exist
#             attr = attribute.Register.get(attr_name)
#             if attr.has_defaults():
#                 self.add_attribute(attr_name, attr.default(self))

#     def is_ready(self):
#         self.sort_attributes()
#         for required in self.require_attributes:
#             if not self.attribute(required):
#                 raise error.NotFound("Could not find required attribute `{}`. "
#                                    "Add `{}` to `{}`.".format(required, required, self.name))
#         for attr in self.attrs:
#             attr.validate_settings()
#             if 'valid' in dir(attr):
#                 attr.valid()

#     def action(self, command):
#         if command not in dir(self):
#             raise error.Bug("Invalid component command {}. "
#                                "This is a bug, report "
#                                "it!".format(command))

#         if command in dir(self):
#             getattr(self, command)()

#     def attribute_action(self, command):
#         for attr in self.attrs:
#             if command in dir(attr):
#                 getattr(attr, command)()

#     def prepare(self):
#         map(lambda attr: attr.prepare(), self.attrs)

#     def sort_attributes(self):
#         util.order(self.attrs, requirement_extractor, name_extractor)
