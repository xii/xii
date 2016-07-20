from xii import attribute, error
from xii.attribute import Key
from xii.output import show_setting


class CountAttribute(attribute.Attribute):
    name = 'count'
    allowed_components = ['node']
    defaults = 1

    keys = Key.Int

    def info(self):
        show_setting('count', self.settings)

    def valid(self):
        if not isinstance(self.settings, int):
            raise error.InvalidAttribute(self.cmpnt.dfn_file, 'node', self.settings)

    def counted_names(self):
        name = self.cmpnt.name
        if self.settings == 1:
            return [name]

        return ["{}-{}".format(name, i) for i in range(1, self.settings + 1)]

attribute.Register.register('count', CountAttribute)
