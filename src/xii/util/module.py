import sys
import os
import imp
import inspect
import importlib
import types
import contextlib

from xii import error

def module_env():
    mods = {}
    filtered = ["xii.attributes", "xii.components", "xii.commands"]
    for name, mod in sys.modules.items():
        if name.startswith("xii.attributes"):
            continue
        if name.startswith("xii.components"):
            continue
        if name.startswith("xii.commands"):
            continue
        mods[name] = mod
    return mods


@contextlib.contextmanager
def additional_sys_path(path: str):
    old_modules = sys.modules.copy()
    old_path = sys.path.copy()
    sys.path.insert(0,path)
    try:
        yield
    finally:
        sys.path = old_path
        sys.modules = old_modules


def new_package(*args):
    name = ".".join(args)
    spec = importlib.machinery.ModuleSpec(name, None, is_package=True)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    return mod

def add_submodule(module, name, *args):
    base_module_path = ".".join(args)
    base_module = importlib.import_module(base_module_path)
    sys.modules[".".join(args + (name,))] = module
    base_module.__dict__[name] = module


def load_module(path, name, *args):
    module_path = ".".join(args + (name,))
    module=None

    if os.path.basename(path) != "__init__.py" or not os.path.exists(path):
        raise error.Bug("Try to load a invalid package path (path was: "
                        "{})".format(path))

    with additional_sys_path(os.path.dirname(path)):
        spec = importlib.util.spec_from_file_location(module_path, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    add_submodule(module, name, *args)
    return module

def classes_from_module(mod, types=[]):
    for _, inst in inspect.getmembers(mod, inspect.isclass):
        base = inspect.getmro(inst)
        ok = True
        for t in types:
            if t not in base:
                ok = False
        if ok:
            yield inst
