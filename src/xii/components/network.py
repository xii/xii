from xii import component, error, paths
from xii.output import show_setting, section

class NetworkComponent(component.Component):
    default_attributes = ['stay']
    require_attributes = ['mode']

    xml_net = {}

    def add_xml(self, section, xml):
        self.xml_net[section] += "\n" + xml

    def start(self):
        net = self.conn().get_network(self.name, raise_exception=False)

        if not net:
            net = self._spawn_network()

    def destroy(self):
        pass

    def suspend(self):
        pass

    def resume(self):
        pass

    def is_ready(self):
        component.Component.is_ready(self)

        found = 0
        for typ in ['nat', 'bridge', 'isolated']:
            if self.attribute(typ):
                found += 1

        if found == 0:
            raise error.DefError("Could not find a valid configuration for {}. "
                                 "Need a network type "
                                 "(e.g 'nat')".format(self.name))

        if found > 1:
            raise error.DefError("Multiple network types define for {}. "
                                 "Only on must selected".format(self.name))

    def _spawn_network(self):
        pass


component.Register.register('network', NetworkComponent)
