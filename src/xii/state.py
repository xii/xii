import os
import yaml


class XiiState():
    state = {'xii': {}}

    def __init__(self, definition, state_file):
        self.definition = definition
        self.state_file = state_file

    def set(self, key, value, group='xii'):
        if group not in self.state.keys():
            self.state[group] = {}

        self.state[group][key] = value

    def get(self, key, group='xii', default=None):
        if group not in self.state.keys():
            return default

        if key not in self.state[group].keys():
            return default

        return self.state[group][key]

    def set_group(self, group, value):
        self.state[group] = value

    def get_group(self, group, default=None):
        if group not in self.state.keys():
            return default

        return self.state[group]

    def load(self):
        if not os.path.isfile(self.state_file):
            raise RuntimeError("Could not load state file. Went something wrong?"
                               "(file was: {}".format(self.state_file))

        try:
            stream = open(self.state_file, 'r')
            content = yaml.load(stream)
        except IOError:
            raise RuntimeError("Could not open state file for reading")
        except yaml.YamlError as err:
            raise RuntimeError("Failed to parse maleformed state file. (file "
                               "was: {}".format(err))
        self.state = content

    def save(self):
        try:
            stream = open(self.state_file, 'w')
            yaml.dump(self.state, stream)
        except IOError:
            raise RuntimeError("Could not open state file.")
