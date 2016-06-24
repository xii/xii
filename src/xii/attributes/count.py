from xii import attribute, error
from xii.output import show_setting


class CountAttribute(attribute.Attribute):
    name = 'count'
    allowed_components = ['node']
    defaults = 1

    def info(self):
        show_setting('count', self.value)

    def valid(self):
        if not isinstance(self.value, int):
            raise error.InvalidAttribute(self.cmpnt.dfn_file, 'node', self.value)

    def counted_names(self):
        name = self.cmpnt.name
        if self.value == 1:
            return [name]

        return ["{}-{}".format(name, i) for i in range(1, self.value + 1)]

attribute.Register.register('count', CountAttribute)
