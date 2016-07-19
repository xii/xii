from xii import error


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


class Key():
    Int, String, Bool, Array, Dict = ((int, "Integer"),
                                      (basestring, "String"),
                                      (bool, "Boolean"),
                                      (list, "List/Array"),
                                      (dict, "Hash/Dictonary"))


class Attribute():
    name = ""
    allowed_components = []
    requires = []

    defaults = None

    keys = {}

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

    def __init__(self, settings, cmpnt):
        self.cmpnt = cmpnt
        self.value = settings
        self.settings = settings

    def conn(self):
        return self.cmpnt.conn()

    def virt(self):
        return self.cmpnt.virt()

    def guest(self, image_path):
        return self.conn().guest(image_path)

    def validate_settings(self):
        for name, defn in self.keys.items():
            if self._requires_key(defn, name, self.value):
                self._check_type(defn, name, self.value[name])

    def setting(self, key):
        if key not in self.settings:
            return None
        return self.settings[key]

    def _requires_key(self, defn, key, value):
            # check if required
            if 'required' in defn:
                if key not in self.value:
                    raise error.DefError("Attribute {} requires {}. But attribute "
                                         "was not found".format(self.name, key))
            if key not in self.value:
                return False
            return True

    def _check_type(self, defn, name, value):

            # Check the rest
            if not isinstance(value, defn['type'][0]):
                raise error.DefError("Attribute {} needs to be a {}".format(name, defn['type'][1]))

            # Check dicts
            if defn['type'][0] == Key.Dict:
                for name, dict_defn in defn.items():
                    if self._requires_key(defn, name, value):
                        self._check_type(dict_defn, name, value[name])

            # Check lists/arrays
            if defn['type'][0] == Key.Array:
                for v in value:
                    self._check_type(defn, name, v)
