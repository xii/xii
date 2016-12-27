import os

from functools import partial

from xii import error, util
from xii.entity import Entity
from xii.component import Component
from xii.attribute import Attribute
from xii.command import Command

# directory structure of a extension
# .
#  components/
#    component1/
#      templates/
#        co1.xml
#      component1.py
#      attributes/
#        attr1/
#         attr1.py
#         templates/
#           a1.xml
#  commands/
#    command1/
#     command1.py
#     templates/
#       co1.xml

class ExtensionManager():

    def __init__(self):
        self._known = {
            "commands": {},
            "attributes": {},
            "components": {}
        }
        self._paths = set()

    def add_path(self, path):
        if not os.path.exists(path):
            raise error.NotFound("Could not find extension path: {}"
                                 .format(path))
        self._paths.add(path)

    def add_builtin_path(self):
        path = os.path.join(os.path.dirname(__file__), "builtin")
        self.add_path(path)

    def load(self):
        for base_path in self._paths:
            commands = os.path.join(base_path, "commands")
            components = os.path.join(base_path, "components")

            if os.path.exists(components):
                self._find_components(components)

            if os.path.exists(commands):
                self._add_commands(commands)

    def _find_components(self, base_path):
        dirs = os.listdir(base_path)
        paths = map(partial(os.path.join, base_path), dirs)

        for name, path in zip(dirs, paths):
            if not os.path.isdir(path):
                continue
            self._load_components(name, path)

            # load all attributes
            attr_path = os.path.join(path, "attributes")
            if not os.path.exists(attr_path):
                continue

            self._find_attributes(name, attr_path)

    def _find_attributes(self, component, base_path):
        dirs = os.listdir(base_path)
        paths = map(partial(os.path.join, base_path), dirs)
        
        for name, path in zip(dirs, paths):
            if (os.path.isdir(path) or
                os.path.splitext(path)[1] == ".py"):
                self._load_attributes(name, component, path)

    def _load_attributes(self, name, component, path):
        module_name = "xii.attribute." + name

        if os.path.basename(path).startswith("__"):
            return

        if os.path.isdir(path):
            path = util.resource_from_path(path)

        classes = util.classes_from_module(module_name, path, [Entity, Attribute])

        for klass in classes:
            if klass.atype == "":
                continue
            if component not in self._known["attributes"]:
                self._known["attributes"][component] = {}

            self._known["attributes"][component][klass.atype] = {
                    "class": klass,
                    "templates": self._find_templates(path)
            }

    def _load_components(self, name, path):
        # load component class
        classes = util.classes_from_module("xii.component." + name,
                                            util.resource_from_path(path),
                                            [Entity, Component])
        for klass in classes:
            # skip base component class
            if klass.ctype == "":
                continue
            self._known["components"][klass.ctype] = {
                    "class": klass,
                    "templates": self._find_templates(path)
            }

    def _add_commands(self, path):
        pass

    def _find_templates(self, path):
        tpl_path = os.path.join(path, "templates/")
        tpls     = {}

        if not os.path.exists(tpl_path):
            return tpls

        for dir, _, files in os.walk(tpl_path):
            name = dir.replace(tpl_path, "")
            for f in files:
                tpls[os.path.join(name, f)] = os.path.join(dir, f)
        return tpls
