import yaml

from output import debug
from xii.component import ComponentRegister
from xii.property import PropertyRegister


def load_from_file(def_file):
    debug("Loading definition file: {}".format(def_file))
    definition = XiiDefinition(def_file)
    definition.load()
    return definition


class XiiDefinition():

    definition = {}

    def __init__(self, def_file):
        self.def_file = def_file

    def load(self):
        try:
            stream = open(self.def_file, 'r')
            self.definition = yaml.load(stream)
        except IOError:
            raise RuntimeError("Could not open definition file. "
                               "(file was: {})".format(self.def_file))
        except yaml.YamlError as err:
            raise RuntimeError("Could not parse definition file. {}".format(err))

    def config(self, key, default=None, group='xii'):
        if group not in self.definition or key not in self.definition[group]:
            return default
        return self.definition[group][key]

    def items(self):
        for component in self.definition:
            name = component.keys()[0]
            settings = component.values()[0]
            if name != 'xii':
                yield (name, settings)

    def validate(self):
        for name, settings in self.items():
            if 'type' not in settings:
                raise RuntimeError("Undefined type for {} component. Add a "
                                   "appropriate type".format(name))

    def components(self):
        self.validate()
        for name, settings in self.items():
            component = ComponentRegister.get_by_name(settings['type'], name, None)
            for prop_name, prop_settings in settings.items():
                prop = PropertyRegister.get_by_name(prop_name, prop_settings, component)

                if not prop:
                    debug("Unkown property `{}`. Skipping.".format(prop_name))
                    continue
                component.add(prop)
            yield component
