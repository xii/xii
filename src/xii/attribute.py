class Register():
    registered = {}

    @classmethod
    def get(cls, name):
        if name not in cls.registered:
            return None
        return cls.registered[name]

    @classmethod
    def register(cls, name, attr):
        cls.registered[name] = attr


class Attribute():
    name = "basic-attribute"
    allowed_components = []
    defaults = None

    @classmethod
    def has_defaults(cls):
        if cls.defaults:
            return True
        return False

    @classmethod
    def default(cls, cmpnt):
        return cls(cls.defaults, cmpnt)

    @classmethod
    def enabled_for(cls, name):
        if name in cls.allowed_components:
            return True
        return False

    def info(self):
        pass

    def __init__(self, value, cmpnt):
        self.cmpnt = cmpnt
        self.value = value

    def conn(self):
        return self.cmpnt.conn

    def virt(self):
        return self.cmpnt.virt()
