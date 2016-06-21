from xii import attribute, error

class Register():
    registered = {}

    @classmethod
    def get(cls, typ):
        if typ not in cls.registered:
            raise RuntimeError("Invalid component `{}`".format(typ))
        return cls.registered[typ]

    @classmethod
    def register(cls, name, klass):
        cls.registered[name] = klass


class Component():
    require_properties = []

    def __init__(self, name, conn, conf):
        self.conn = conn
        self.attrs = {}
        self.name = name
        self.conf = conf

    def add_attribute(self, attr):
        self.attrs[attr.name] = attr

    def virt(self):
        return self.conn.virt()

    def attribute(self, name):
        if name not in self.attrs:
            klass = attribute.Register.get('count')
            if not klass:
                raise error.Bug(__file__, "Could not find attribute `{}`".format(name))
            if klass.has_defaults():
                return klass.default(self)
            raise RuntimeError("Attribute `{}` has not defaults.".format(name))
        return self.attrs[name]

    def is_ready(self):
        for required in self.require_properties:
            if required not in self.attrs:
                raise RuntimeError("Could not find required attribute `{}`. "
                                   "Add `{}` to `{}`.".format(required, required, self.name))
        for attr in self.attrs:
            if 'valid' in dir(attr):
                attr.valid()

    def action(self, command):
        if command not in ['start']:
            raise RuntimeError("Invalid componenten Command. This is a bug, "
                               "report it!")

        for attr in self.attrs:
            if command in dir(attr):
                getattr(attr, command)()

        if command in dir(self):
            getattr(self, command)()
