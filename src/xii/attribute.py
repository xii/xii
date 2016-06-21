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


class Priority():
    lowest = 1000
    low = 800
    middle = 400
    high = 200
    highest = 100
    first = 10


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

    def __init__(self, settings, cmpnt):
        self.cmpnt = cmpnt
        self.settings = settings
