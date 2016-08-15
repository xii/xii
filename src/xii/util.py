import pkgutil
import inspect
import yaml
import time


from xii import error
from xii.ui import warn


def safe_get(name, structure):
    if name not in structure:
        return None
    return structure[name]


def file_read(path):
    try:
        with open(path, 'r') as stream:
            return stream.read()
    except IOError:
        raise error.NotFound("Could not open `{}`: No such file or "
                             "directory".format(path))


def yaml_read(path):
    try:
        with open(path, 'r') as stream:
            return yaml.load(stream)
    except IOError:
        raise error.DefError("Could not open definition: No such file or directory")
    except yaml.YAMLError as err:
        raise error.ValidatorError("Error parsing definition: {}".format(err))


def load_modules(path):
    modules = []
    for loader, module_name, _ in pkgutil.walk_packages(path):
        module = loader.find_module(module_name).load_module(module_name)

        for name, _ in inspect.getmembers(module):
            if name.startswith('__'):
                continue
            modules.append(name)
    return modules


def wait_until_active(obj, state=1, timeout=5):
    for _ in range(timeout):
        if obj.isActive() == state:
            return True
        time.sleep(1)
    return False


def wait_until_inactive(obj, state=0, timeout=5):
    return wait_until_active(obj, state, timeout)


def domain_has_state(domain, state):
    return domain.state()[0] == state


def domain_wait_state(domain, state, timeout=5):
    for _ in range(timeout):
        if domain_has_state(domain, state):
            return True
        time.sleep(1)
    return False
