from xii import attribute, error, util
from xii.output import debug, HasOutput

from multiprocessing import Process


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


class Component(HasOutput, Process):
    require_attributes = []
    default_attributes = []

    def ident(self):
        return [self.component_name]

    def __init__(self, name, conn, conf):
        self.connection = conn
        self.attrs = []
        self.name = name
        self.component_name = name
        self.conf = conf
        self.prepare()

    def add_attribute(self, name, attr):
        for idx, a in enumerate(self.attrs):
            if a.attr_name == name:
                self.attrs[idx] = attr
                return
        self.attrs.append(attr)

    def virt(self):
        return self.conn().virt()

    def conn(self):
        return self.connection

    def attribute(self, name):
        for attr in self.attrs:
            if attr.attr_name == name:
                return attr
        debug("Could not find attribute {}".format(name))
        return None

    def add_default_attributes(self):
        for attr_name in self.default_attributes:
            # Assume default attributes must exist
            attr = attribute.Register.get(attr_name)
            if attr.has_defaults():
                self.add_attribute(attr_name, attr.default(self))

    def is_ready(self):
        self.sort_attributes()
        for required in self.require_attributes:
            if not self.attribute(required):
                raise error.NotFound("Could not find required attribute `{}`. "
                                   "Add `{}` to `{}`.".format(required, required, self.name))
        for attr in self.attrs:
            attr.validate_settings()
            if 'valid' in dir(attr):
                attr.valid()

    def action(self, command):
        if command not in dir(self):
            raise error.Bug("Invalid component command {}. "
                               "This is a bug, report "
                               "it!".format(command))

        if command in dir(self):
            getattr(self, command)()

    def attribute_action(self, command):
        for attr in self.attrs:
            if command in dir(attr):
                getattr(attr, command)()

    def prepare(self):
        map(lambda attr: attr.prepare(), self.attrs)

    def sort_attributes(self):
        def name_extractor(objs, name):
            for idx, obj in enumerate(objs):
                if obj.attr_name == name:
                    return idx
            return None

        def requirement_extractor(objs, idx):
            return objs[idx].requires
        util.order(self.attrs, requirement_extractor, name_extractor)
