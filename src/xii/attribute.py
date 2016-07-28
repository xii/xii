class Register():
    registered = {}

    @classmethod
    def get(cls, name):
        if name not in cls.registered:
            return None
        return cls.registered[name]

    @classmethod
    def register(cls, attr):
        cls.registered[attr.attr_name] = attr


class Attribute():
    attr_name = ""
    allowed_components = []
    requires = []

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
    def enabled_for(cls, name):
        if name in cls.allowed_components:
            return True
        return False

    @classmethod
    def register(cls):
        Register().register(cls)

    def info(self):
        pass

    def __init__(self, settings, cmpnt):
        self.cmpnt = cmpnt
        self.name = cmpnt.name
        self.settings = settings

    def conn(self):
        return self.cmpnt.conn()

    def virt(self):
        return self.cmpnt.virt()

    def guest(self, image_path):
        return self.conn().guest(image_path)

    def setting(self, path):
        value = self.settings
        for key in path.split("/"):
            if key not in value:
                return None
            value = value[key]
        return value

    def validate_settings(self):
        self.keys.validate(self.name + " > " + self.attr_name, self.settings)
