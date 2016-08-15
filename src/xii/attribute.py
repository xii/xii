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

    def __init__(self, settings, component):
        Entity.__init__(self, name=self.entity,
                              parent=component)
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

    def component_name(self):
        return self.get_parent().name

    def validate(self):
        self.keys.validate(self.get_parent().name + " > " + self.name, self.settings)
