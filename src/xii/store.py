class Store():

    def __init__(self, parent={}):
        self._values = parent

    def set(self, key, new):
        path = key.split("/")
        value = self._values
        for node in path[:-1]:
            value = value[node]

        value[path[-1]] = new

    def get(self, key):
        path = key.split("/")
        value = self._values
        for node in path:
            value = value[node]
        return value

    def derive(self, key):
        return Store(parent=self.get(key))
