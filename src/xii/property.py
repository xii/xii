

class PropertyRegister():
    registered = {}

    @classmethod
    def get_by_name(cls, name, settings, component):
        if name not in cls.registered:
            return None
        return cls.registered[name](settings, component)

    @classmethod
    def register(cls, name, prop):
        cls.registered[name] = prop


class PropertyPriority():
    lowest = 1000
    low = 800
    middle = 400
    high = 200
    highest = 100
    first = 10

class Property():
    name = "basic-property"
    allowed_components = []
    priority = PropertyPriority.middle

    @classmethod
    def enabled_for(cls, name):
        if name in cls.allowed_components:
            return True
        return False

    def __init__(self, settings, component):
        self.component = component
        self.settings = settings
