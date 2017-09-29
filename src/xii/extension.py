import os

from xii import error, util
from xii.entity import Entity
from xii.component import Component
from xii.attribute import Attribute
from xii.command import Command

class ExtensionManager:
    """
    Loads all extensions (commands, components, attributes)

    Try to load a directory structure which looks like:
    ::

        path/
        |
        |---- commands/
        |     |---- command1/
        |     |     |---- __init__.py
        |     |     '---- ...
        |     |---- ...
        |     '---- commandN
        |
        '---- components/
              |---- component1/
              |     |---- __init__.py
              |     |---- ...
              |     |
              |     '---- attributes/
              |           |---- attribute1
              |           |     |---- __init__.py
              |           |     '---- ...
              |           '---- attributeN
              '---- componentN

    each subdirectory can have a 'templates/' directory containing all
    templates to be loaded

    Note: classes/methods from component exports can be accessed via
    "xii.components.<component name>.<target>" the same for attributes
    and commands:
        "xii.attributes.<component name>.<target>" or "xii.commands.<target>"
    """

    def __init__(self):
        self._known = {
            "commands": [],
            "attributes": {},
            "components": {}
        }
        self._paths = set()

        self._init_namespaces()

    def _init_namespaces(self):
        namespaces = ["commands", "attributes", "components"]
        for ns in namespaces:
            ns_mod = util.new_package("xii", ns)
            util.add_submodule(ns_mod, ns, "xii")

    def add_path(self, path):
        if not os.path.exists(path):
            raise error.NotFound("Could not find extension path: {}"
                                 .format(path))
        self._paths.add(path)

    def add_builtin_path(self):
        path = os.path.join(os.path.dirname(__file__), "builtin")
        self.add_path(path)

    def get_command(self, name):
        if name is None:
            return None
        for cmd in self._known["commands"]:
            if name in cmd["class"].name:
                return cmd
        return None

    def get_commands(self):
        return self._known["commands"]

    def get_component(self, name):
        if name not in self._known["components"]:
            return None
        return self._known["components"][name]

    def get_components(self):
        return self._known["components"].values()

    def get_attribute(self, component, name):
        if component not in self._known["attributes"]:
            return None

        if name not in self._known["attributes"][component]:
            return None
        return self._known["attributes"][component][name]

    def get_attributes(self, component):
        if component not in self._known["attributes"]:
            return None
        return self._known["attributes"][component].values()

    def load(self):
        for base_path in self._paths:
            commands = os.path.join(base_path, "commands")
            components = os.path.join(base_path, "components")

            if os.path.exists(components):
                self._load_components(components)

            if os.path.exists(commands):
                self._load_commands(commands)

    def _collect_paths(self, base_path):
        if not os.path.exists(base_path):
            return []

        for dir in os.listdir(base_path):
            path = os.path.join(base_path, dir)
            if not os.path.isdir(path):
                continue
            if dir.startswith("__"):
                continue
            yield (dir, path)

    def _load_commands(self, base_path):
        for name, path in self._collect_paths(base_path):
            init = os.path.join(path, "__init__.py")
            mod = util.load_module(init, name, "xii", "commands")

            classes = util.classes_from_module(mod, [Entity, Command])

            for cmd in classes:
                # FIXME: Find a better way to check if base class was detected
                if cmd.name == "":
                    continue
                self._known["commands"].append({
                    "class": cmd,
                    "templates": self._find_templates(path)
                    })

    def _load_components(self, base_path):
        for name, path in self._collect_paths(base_path):
            init = os.path.join(path, "__init__.py")
            mod = util.load_module(init, name, "xii", "components")

            classes = util.classes_from_module(mod, [Entity, Component])

            for cmpnt in classes:
                # FIXME: Find a better way to check if base class was detected
                if cmpnt.ctype == "":
                    continue
                self._known["components"][cmpnt.ctype] = {
                    "class": cmpnt,
                    "templates": self._find_templates(path)
                    }
            self._load_attributes(path, name)

    def _load_attributes(self, component_path, component):
        base_path = os.path.join(component_path, "attributes")
        base_mod = util.new_package("xii", "attributes", component)
        util.add_submodule(base_mod, component, "xii", "attributes")

        for name, path in self._collect_paths(base_path):
            init = os.path.join(path, "__init__.py")
            mod = util.load_module(init, name, "xii", "attributes", component)
            classes = util.classes_from_module(mod, [Entity, Attribute])

            for attr in classes:
                # FIXME: Find a better way to check if base class was detected
                if attr.atype == "":
                    continue
                if component not in self._known["attributes"]:
                    self._known["attributes"][component] = {}

                self._known["attributes"][component][attr.atype] = {
                    "class": attr,
                    "templates": self._find_templates(path)
                    }

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
