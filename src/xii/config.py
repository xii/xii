
from xii import util


def load_from_file(path):
    yaml = util.yaml_read(path)
    return Config(yaml)


class Config():
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        if key not in self._values:
            return default
        return self._values[key]

    def default_host(self):
        return self.get('default_host')

    def workers(self):
        return self.get('parallel_workers', 3)

    def wait(self, default=3):
        return self.get('retry_after', default)

    def retry(self, case, default=20):
        return self.get(case + '_retry', default)
