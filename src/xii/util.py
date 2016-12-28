import sys
import os
import pkgutil
import inspect
import imp
import yaml
import jinja2
import time
import md5
import ast

from Crypto.PublicKey import RSA

from xii import error


def safe_get(name, structure):
    if name not in structure:
        return None
    return structure[name]


def convert_type(convertable):
    if convertable in ["true", "True", "TRUE"]:
        return True
    if convertable in ["false", "False", "FALSE"]:
        return False
    try:
        return ast.literal_eval(convertable)
    except ValueError:
        return convertable


def file_read(path):
    try:
        with open(path, 'r') as stream:
            return stream.read()
    except IOError:
        raise error.NotFound("Could not open `{}`: No such file or "
                             "directory".format(path))


def md5digest(input):
    return md5.new(input).hexdigest()


def make_temp_name(seed):
    hashed = md5digest(seed + str(time.time()))
    return "/tmp/xii-" + hashed


def jinja_read(tpl, store):
    try:
        path, filename = os.path.split(tpl)
        from_file = jinja2.FileSystemLoader(path)
        env = jinja2.Environment(loader=from_file,
                                 undefined=jinja2.StrictUndefined)

        yml = env.get_template(filename).render(store.values())

        return yaml.load(yml)
    except IOError:
        raise error.ConnError("Could not open definition: "
                              "No such file or directory")
    except yaml.YAMLError as err:
        raise error.ValidatorError("error parsing definition, {}".format(err))
    except jinja2.exceptions.UndefinedError as err:
        raise error.ValidatorError("error parsing definition, {}".format(err))


def yaml_read(path):
    try:
        with open(path, 'r') as stream:
            return yaml.load(stream)
    except IOError:
        raise error.ConnError("Could not open definition: "
                              "No such file or directory")
    except yaml.YAMLError as err:
        raise error.ValidatorError("Error parsing definition: {}".format(err))


def yaml_write(path, obj):
    try:
        with open(path, 'w') as hdl:
            yaml.dump(obj, hdl, default_flow_style=False)
    except IOError as err:
        raise error.ExecError("Could not write yaml file: {}".format(err))
    except yaml.YAMLError as err:
        raise error.ExecError("Could not write yaml file: {}".format(err))

def new_namespace(name):
    mod = imp.new_module(name)
    sys.modules[name] = mod

def load_modules(paths):
    modules = []

    for loader, module_name, _ in pkgutil.walk_packages(paths):
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


def generate_rsa_key_pair():
    rsa = RSA.generate(4096)
    pub = rsa.publickey()
    return (rsa.exportKey("PEM"), pub.exportKey("OpenSSH"))


def parse_passwd(passwd):
    users = {}

    for line in passwd:
        user = line.split(":")
        if len(user) < 6:
            continue
        users[user[0]] = {
            'uid': int(user[2]),
            'gid': int(user[3]),
            'description': user[4],
            'home': user[5],
            'shell': user[6]
        }
    return users


def parse_groups(group):
    groups = {}

    for line in group:
        group = line.split(":")
        if len(group) < 2:
            continue

        groups[group[0]] = {'gid': int(group[2]), 'users': []}

        if len(group) > 2:
            groups[group[0]]['users'] = group[3].split(',')
    return groups


def resource_from_path(path, ext=".py"):
    name = os.path.basename(path)
    return os.path.join(path, name + ext)


def load_module(module_name, path):

    if os.path.basename(path) == "__init__.py":
        path = os.path.dirname(path)

    # try:
    if os.path.isdir(path):
        mod_info = ("py", "r", imp.PKG_DIRECTORY)
        mod = imp.load_module(module_name, None, path, mod_info)
    else:
        mod_info = ("py", "r", imp.PY_SOURCE)
        with open(path, "r") as module_file:
            mod = imp.load_module(module_name, module_file, path, mod_info)
    # except Exception:
    #     raise error.ExecError("Could not load extension: {}".format(path))
    return mod


def classes_from_module(mod, types=[]):
    for _, inst in inspect.getmembers(mod, inspect.isclass):
        base = inspect.getmro(inst)
        ok = True
        for t in types:
            if t not in base:
                ok = False
        if ok:
            yield inst
