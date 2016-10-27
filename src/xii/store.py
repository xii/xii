from abc import ABCMeta, abstractmethod

class Store():

    def __init__(self, parent={}):
        self._values = parent

    def set(self, key, new):
        path = key.split("/")
        value = self._values
        for node in path[:-1]:
            # generate path if not exist yet
            if not node in value:
                value[node] = {}
            value = value[node]

        value[path[-1]] = new

    def get(self, key, default=None):
        path = key.split("/")
        value = self._values
        try:
            for node in path:
                value = value[node]
            return value
        except KeyError:
            return default

    def merge(self, iteratable, overwrite=True, root=None):
        values = self._values
        if root:
            values = self._values[root]
        
        for key, value in iteratable.items():
            if not overwrite and key in values:
                continue
            values[key] = value
        
    def derive(self, key):
        return Store(parent=self.get(key))

    def values(self):
        return self._values

    def dump(self):
        import pprint
        pprint.pprint(self._values)


class HasStore():
    __meta__ = ABCMeta

    @abstractmethod
    def store(self):
        pass

    def get(self, key, default=None):
        return self.store().get(key, default)

    def set(self, key, value):
        return self.store().set(key, value)
