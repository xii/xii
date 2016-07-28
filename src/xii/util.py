import pkgutil
import inspect
import yaml
import time


from xii import error
from xii.output import debug


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


def get_users(guest):
    users = {}
    content = guest.cat('/etc/passwd').split("\n")

    for line in content:
        user = line.split(":")
        if len(user) < 6:
            continue
        users[user[0]] = {
                'uid': int(user[2]),
                'gid': int(user[3]),
                'description': user[4],
                'home': user[5],
                'shell': user[6]}
    return users


def get_groups(guest):
    groups = {}
    content = guest.cat('/etc/group').split("\n")

    for line in content:
        group = line.split(":")
        if len(group) < 2:
            continue

        groups[group[0]] = {'gid': int(group[2]), 'users': []}

        if len(group) > 2:
            groups[group[0]]['users'] = group[3].split(',')
    return groups


def order(objs, requirement_extractor, name_extractor):
    if not isinstance(objs, list):
        raise error.Bug("order: objs is not a list")

    idx = 0
    rounds = 0
    size = len(objs)

    while idx != size:
        has_moved = False
        if rounds > size * 2:
            raise error.Bug("Cyclic dependencies.")

        for requirement in requirement_extractor(objs, idx):
            move = name_extractor(objs, requirement)
            if move is None:
                debug("Requirement {} does not exist".format(requirement))
                continue

            if move > idx:
                objs.insert(idx, objs.pop(move))
                has_moved = True
        if not has_moved:
            idx += 1
        rounds += 1
