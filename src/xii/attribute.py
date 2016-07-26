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
    Int, String, Bool, Array, Dict = ((int, "integer"),
                                      (basestring, "string"),
                                      (bool, "boolean"),
                                      (list, "list/array"),
                                      (dict, "hash/dictonary"))


class Attribute():
    allowed_components = []
    requires = []

    defaults = None

    keys = {}

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

    def validate_settings(self):
        if isinstance(self.keys, tuple):
            if not isinstance(self.settings, self.keys[0]):
                raise error.DefError("Attribute '{}' needs to be of type {}".format(self.name, self.keys[1]))
            return

        for name, defn in self.keys.items():
            if self._requires_key(defn, self.name + " > " + name, name, self.settings):
                self._check_type(defn, self.name + " > " + name, name, self.settings[name])

    def setting(self, path):
        value = self.settings
        for key in path.split("/"):
            if key not in value:
                return None
            value = value[key]
        return value

    def _requires_key(self, defn, name, key, value):
            if 'required' in defn:
                if key not in value:
                    raise error.DefError("Attribute '{}' requires {}. But attribute "
                                         "was not found".format(self.name, key))
            if key not in value:
                return False
            return True

    def _check_type(self, defn, name, key, value):
            # Check the rest
            if not isinstance(value, defn['type'][0]):
                raise error.DefError("Attribute '{}' needs to be a {}".format(name, defn['type'][1]))
            # Check dicts
            if defn['type'] == Key.Dict:
                for iname, idefn in defn['keys'].items():
                    if self._requires_key(idefn, name + " > " + iname, iname, value):
                        self._check_type(idefn, name + " > " + iname, iname, value[iname])

            # Check lists/arrays
            if defn['type'] == Key.Array:
                for v in value:
                    if not isinstance(v, defn['keys'][0]):
                            raise error.DefError("Attribute '{}' list items must "
                                                 "be {}".format(name, defn['keys'][1]))
