from xii import attribute, error
from xii.output import debug


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
        self.attrs = []
        self.name = name
        self.conf = conf

    def add_attribute(self, attr):
        self.attrs.append((attr.name, attr))

    def virt(self):
        return self.conn().virt()

    def conn(self):
        return self.connection

    def attribute(self, name):
        for attr_name, attr in self.attrs:
            if attr_name == name:
                return attr
        debug("Could not find attribute {}".format(name))
        return None

    def is_ready(self):
        for attr_name in self.default_attributes:
            if attr_name not in self.attrs:
                attr = attribute.Register.get(attr_name)
                self.add_attribute(attr.default(self))

        self.sort_attributes()

        for required in self.require_attributes:
            if not self.attribute(required):
                raise RuntimeError("Could not find required attribute `{}`. "
                                   "Add `{}` to `{}`.".format(required, required, self.name))
        for attr in self.attrs:
            attr[1].validate_settings()
            if 'valid' in dir(attr[1]):
                attr[1].valid()

    def action(self, command):
        if command not in dir(self):
            raise RuntimeError("Invalid component command {}. "
                               "This is a bug, report "
                               "it!".format(command))

        if command in dir(self):
            getattr(self, command)()

    def attribute_action(self, command, settings):
        for _, attr in self.attrs:
            if command in dir(attr):
                getattr(attr, command)(settings)

    def info(self):
        map(lambda attr: attr[1].info(), self.attrs)

    def sort_attributes(self):
        idx = 0
        rounds = 0
        size = len(self.attrs)

        while idx != size:
            has_moved = False
            if rounds > size * 2:
                raise error.Bug("Cyclic attribute dependency. "
                                "This should never happen")

            for required in [attr[1].requires for attr in self.attrs]:
                try:
                    move = [attr[0] for attr in self.attrs].index(required)

                    if move > idx:
                        self.attrs.insert(idx, self.attrs.pop(move))
                        has_moved = True
                except ValueError:
                    debug("Required attribute {} not found. "
                          "Skipping!".format(required))
                    continue
            if not has_moved:
                idx += 1
            rounds += 1
