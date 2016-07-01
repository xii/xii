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
    require_attributes = []
    default_attributes = []

    def __init__(self, name, conn, conf):
        self.connection = conn
        self.attrs = {}
        self.name = name
        self.conf = conf

    def add_attribute(self, attr):
        self.attrs[attr.name] = attr

    def virt(self):
        return self.conn().virt()

    def conn(self):
        return self.connection

    def attribute(self, name):
        if name not in self.attrs:
            raise error.Bug(__file__, "Can not find attribute {} but required".format(name))
        return self.attrs[name]

    def is_ready(self):
        for attr_name in self.default_attributes:
            if attr_name not in self.attrs:
                attr = attribute.Register.get(attr_name)
                self.add_attribute(attr.default(self))

        for required in self.require_attributes:
            if required not in self.attrs:
                raise RuntimeError("Could not find required attribute `{}`. "
                                   "Add `{}` to `{}`.".format(required, required, self.name))
        for attr in self.attrs:
            if 'valid' in dir(attr):
                attr.valid()

    def action(self, command):
        if command not in dir(self):
            raise RuntimeError("Invalid component command {}. "
                               "This is a bug, report "
                               "it!".format(command))

        if command in dir(self):
            getattr(self, command)()

    def attribute_action(self, command, settings):
        for attr in self.attrs.values():
            if command in dir(attr):
                getattr(attr, command)(settings)

    def info(self):
        map(lambda attr: attr.info(), self.attrs.values())
