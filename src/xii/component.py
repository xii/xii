from xii.output import debug


class ComponentRegister():
    registered = {}

    @classmethod
    def get_by_name(cls, name, comp_name, connection):
        if name not in cls.registered:
            raise RuntimeError("Invalid component `{}`".format(name))
        return cls.registered[name](comp_name, connection)

    @classmethod
    def register(cls, name, klass):
        cls.registered[name] = klass


class Component():
    require_properties = []

    def __init__(self, name, connection):
        self.connection = connection
        self.properties = {}
        self.name = name

    def add(self, prop):
        self.properties[prop.name] = prop

    def is_ready(self):
        for required in self.require_properties:
            if required not in self.properties:
                raise RuntimeError("Could not find required property `{}`. "
                                   "Add `{}` to `{}`.".format(required, required, self.name))
        return True

    def action(self, command):
        if command not in ['start']:
            raise RuntimeError("Invalid componenten Command. This is a bug, "
                               "report it!")
        for prop in self.properties:
            if command in dir(prop):
                getattr(prop, command)()

        if command in dir(self):
            getattr(self, command)()
