import os

from xii import util, error


def find_file(path=None):
    if not path:

        cwd = os.getcwd()
        path = os.path.join(cwd, os.path.basename(cwd) + ".xii")

        if os.path.exists(path):
            return path
        else:
            raise RuntimeError("Could not find a sustainable xii definition")
    else:
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise RuntimeError("Could not open xii definition. "
                                "No such file or directory")
        return path


def from_file(dfn_file, conf):
    return Definition(find_file(dfn_file), conf)


class Definition():
    def __init__(self, dfn_file, conf):
        self.dfn_file = dfn_file
        self.dfn = util.yaml_read(self.dfn_file)
        self.conf = conf

    def settings(self, key, default=None, group='xii'):
        if group not in self.dfn or key not in self.dfn[group]:
            return default
        return self.dfn[group][key]

    def items(self):
        for (name, item) in self.dfn.items():
            if name != "xii":
                yield (name, item)

    def item(self, name):
        # Support components with more than one instance
        find_counted= name.split("#")
        if len(find_counted) != 1:
            name = "".join(find_counted[:-1])

        if name not in self.dfn:
            return None
        return self.dfn[name]

    def validate(self):
        for name, settings in self.items():
            if 'type' not in settings:
                raise error.InvalidAttribute(self.dfn_file, 'type', name)

    def file_path(self):
        return self.dfn_file
