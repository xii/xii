from xii import util, error


def from_file(dfn_file, conf):
    return Definition(dfn_file, conf)


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
        for cmpnt_dfn in self.dfn:
            name = cmpnt_dfn.keys()[0]
            settings = cmpnt_dfn.values()[0]
            if name != 'xii':
                yield (name, settings)

    def validate(self):
        for name, settings in self.items():
            if 'type' not in settings:
                raise error.InvalidAttribute(self.dfn_file, 'type', name)

    def file_path(self):
        return self.dfn_file
