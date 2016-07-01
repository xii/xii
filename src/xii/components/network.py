from xii import component
from xii.output import show_setting

class NetworkComponent(component.Component):

    def info(self):
        show_setting('network', self.value)


    pass


component.Register.register('network', NetworkComponent)
