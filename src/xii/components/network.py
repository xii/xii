from xii import component, error, paths
from xii.output import show_setting, section

class NetworkComponent(component.Component):
    default_attributes = ['stay']
    require_attributes = ['mode']

    xml_net = []

    def add_xml(self, xml):
        self.xml_net.append(xml)

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

    def _spawn_network(self):
        self.attribute_action('spawn')
        replace = {'config': "\n".join(self.xml_net),
                   'name': self.name}

        tpl = paths.template('network-component.xml')
        xml = tpl.safe_substitute(replace)
        print(xml)



component.Register.register('network', NetworkComponent)
