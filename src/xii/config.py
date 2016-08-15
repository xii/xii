import yaml
import paths

from xii import error


class Config():

    def __init__(self, path, args):
        self._path = path
        self._args = args
        if not path:
            self._path = paths.local('config.yml')

        try:
            with open(self._path, 'r') as stream:
                self.config = yaml.load(stream)
        except IOError as err:
            raise error.ConnError("Could not load configuration: {}"
                                  .format(err))
        except yaml.YamlError as err:
            raise error.ValidatorError("Could not parse configuration: {}"
                                       .format(err))

    def get(self, key, default=None):
        if key not in self.config:
            self.config[key] = default
            return default
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value
        self.save()
        return self.config[key]

    def save(self):
        try:
            with open(self._path, 'w') as stream:
                yaml.dump(self.config, stream)
        except IOError:
            raise RuntimeError("Could not save configuration")
        except yaml.YamlError as err:
            raise RuntimeError("BUG: Could not save yaml config: {}".format(err))



    def known_hosts(self, add_name=None, add_hosts=None):
        hosts = self.get('known_hosts')
        if not add_name and add_hosts:
            return hosts

        hosts[add_name] = add_hosts
        return self.set('known_hosts', hosts)

    def default_host(self):
        name = self.get('default_host')

        if name not in self.known_hosts():
            raise RuntimeError("Unknown default host `{}`. Check your "
                               "Configuration".format(name))
        return self.known_hosts()[name]

    def is_parallel(self):
        if self._args.no_parallel:
            return False
        return self.get('parallel', True)

    def workers(self):
        return self.get('parallel_workers', 3)
