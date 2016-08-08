from xii.output import HasOutput
from xii.entity import EntityRegister, Entity

class Attribute(Entity):
    entity = "attribute"

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

    @classmethod
    def register(cls):
        EntityRegister.register("attribute", cls)

    def __init__(self, settings, component):
        print("initialize {}".format(self.entity))
        Entity.__init__(self, name=self.entity,
                              parent=component)
        print(self._parent)
        self.settings = settings

    def share(self, name, creator, finalizer=None):
        return self.get_parent().share(name, creator, finalizer)

    def setting(self, path, default_value=None):
        value = self.settings
        for key in path.split("/"):
            if key not in value:
                return default_value
            value = value[key]
        return value

    def validate(self):
        self.keys.validate(self.get_parent().name + " > " + self.name, self.settings)


# class Attribute(HasOutput):
#     attr_name = ""
#     allowed_components = []
#     requires = []

#     defaults = None

#     keys = None

#     @classmethod
#     def has_defaults(cls):
#         if cls.defaults is None:
#             return False
#         return True

#     @classmethod
#     def default(cls, cmpnt):
#         return cls(cls.defaults, cmpnt)

#     @classmethod
#     def enabled_for(cls, name):
#         if name in cls.allowed_components:
#             return True
#         return False

#     @classmethod
#     def register(cls):
#         Register().register(cls)

#     def ident(self):
#         return [self.cmpnt.name, self.attr_name]

#     def add_info(self, key, value):
#         print("adding {}".format(key))
#         self.cmpnt.add_info(key, value)

#     def __init__(self, settings, cmpnt):
#         self.cmpnt = cmpnt
#         self.name = cmpnt.name
#         self.settings = settings

#     def conn(self):
#         return self.cmpnt.conn()

#     def virt(self):
#         return self.cmpnt.virt()

#     def guest(self, image_path):
#         return self.conn().guest(image_path)

#     def prepare(self):
#         pass

#     def setting(self, path, default_value=None):
#         value = self.settings
#         for key in path.split("/"):
#             if key not in value:
#                 return default_value
#             value = value[key]
#         return value

#     def validate_settings(self):
#         self.keys.validate(self.name + " > " + self.attr_name, self.settings)
