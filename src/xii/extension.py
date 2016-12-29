import os
from functools import partial

from xii import error, util
from xii.entity import Entity
from xii.component import Component
from xii.attribute import Attribute
from xii.command import Command


class ExtensionManager():
    """
    Loads all extensions (commands, components, attributes)

    Try to load a directory structure which looks like:

        path/
        |---- commands/
        |---- command1/
        |     |---- __init__.py
        |     |     '---- ...
        |     |---- ...
        |     '---- commandN
        '---- components/
              |---- __init__.py
              |---- ...
              '---- attributes/
                    |---- attribute1
                    |     |---- __init__.py
                    |     '---- ...
                    '---- attributeN

    each subdirectory can have a 'templates/' directory containing all
    templates to be loaded

    Note: classes/methods from component exports can be accessed via
    "xii.components.<component name>.<target>"
    """

    def __init__(self):
        self._known = {
            "commands": [],
            "attributes": {},
            "components": {}
        }
        self._paths = set()
        util.new_namespace("xii.components")
        util.new_namespace("xii.attributes")

    def add_path(self, path):
        if not os.path.exists(path):
            raise error.NotFound("Could not find extension path: {}"
                                 .format(path))
        self._paths.add(path)

    def add_builtin_path(self):
        path = os.path.join(os.path.dirname(__file__), "builtin")
        self.add_path(path)

    def get_command(self, name):
        for cmd in self._known["commands"]:
            if name in cmd["class"].name:
                return cmd
        return None

    def commands_available(self):
        output = ["", "shortcut  action    description",
                  "-------------------------------"]

        for command in [c["class"] for c in self._known["commands"]]:
            output.append(" {:9}{:10}{}".format(", ".join(command.name[1:]), command.name[0], command.help))
        output.append(" ")
        return output


    def get_component(self, name):
        if name not in self._known["components"]:
            return None
        return self._known["components"][name]

    def get_attribute(self, component, name):
        if component not in self._known["attributes"]:
            return None

        if name not in self._known["attributes"][component]:
            return None
        return self._known["attributes"][component][name]

    def load(self):
        for base_path in self._paths:
            commands = os.path.join(base_path, "commands")
            components = os.path.join(base_path, "components")

            if os.path.exists(components):
                self._find_components(components)

            if os.path.exists(commands):
                self._find_commands(commands)

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
        module_name = "xii.attributes." + component
        mod = util.load_module(module_name, path)
        classes = util.classes_from_module(mod, [Entity, Attribute])

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
        mod = util.load_module("xii.components." + name, path)
        classes = util.classes_from_module(mod, [Entity, Component])

        for klass in classes:
            # skip base component class
            if klass.ctype == "":
                continue
            util.new_namespace("xii.attributes." + name)
            self._known["components"][klass.ctype] = {
                "class": klass,
                "templates": self._find_templates(path)
            }

    def _find_commands(self, base_path):
        dirs = os.listdir(base_path)
        paths = map(partial(os.path.join, base_path), dirs)

        for name, path in zip(dirs, paths):
            if not os.path.isdir(path):
                continue
            self._load_commands(name, path)

    def _load_commands(self, name, path):
        mod = util.load_module("xii.commands." + name, path)
        classes = util.classes_from_module(mod, [Entity, Command])

        for klass in classes:
            if klass.name == []:
                continue
            self._known["commands"].append({
                "class": klass,
                "templates": self._find_templates(path)
            })

    def _find_templates(self, path):
        tpl_path = os.path.join(path, "templates/")
        tpls = {}

        if not os.path.exists(tpl_path):
            return tpls

        for dir, _, files in os.walk(tpl_path):
            name = dir.replace(tpl_path, "")
            for f in files:
                tpls[os.path.join(name, f)] = os.path.join(dir, f)
        return tpls
