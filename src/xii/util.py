import pkgutil
import inspect
import yaml

import libvirt

from xii import error


def file_read(path):
    try:
        with open(path, 'r') as stream:
            return stream.read()
    except IOError:
        raise error.FileError(path, "Could not open file")


def yaml_read(path):
    try:
        with open(path, 'r') as stream:
            return yaml.load(stream)
    except IOError:
        raise error.FileError(path, "Could not open definition file")
    except yaml.YamlError as err:
        raise error.ParseError(path, err)


def yaml_write(path, value):
    pass


def load_modules(path):
    modules = []
    for loader, module_name, _ in pkgutil.walk_packages(path):
        module = loader.find_module(module_name).load_module(module_name)

        for name, _ in inspect.getmembers(module):
            if name.startswith('__'):
                continue
            modules.append(name)
    return modules
