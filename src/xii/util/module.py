import sys
import os
import imp
import inspect

from xii import error

def new_namespace(name):
    mod = imp.new_module(name)
    sys.modules[name] = mod


def load_module(module_name, path):

    if os.path.basename(path) == "__init__.py":
        path = os.path.dirname(path)

    try:
        if os.path.isdir(path):
            mod_info = ("py", "r", imp.PKG_DIRECTORY)
            mod = imp.load_module(module_name, None, path, mod_info)
        else:
            mod_info = ("py", "r", imp.PY_SOURCE)
            with open(path, "r") as module_file:
                mod = imp.load_module(module_name, module_file, path, mod_info)
    except Exception:
        raise error.ExecError("Could not load extension: {}".format(path))
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
