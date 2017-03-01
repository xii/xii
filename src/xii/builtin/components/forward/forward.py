import libvirt

from xii import error
from xii.component import Component
from xii.need import NeedLibvirt, NeedIO
from xii.util import flatten


class ForwardComponent(Component, NeedLibvirt, NeedIO):
    """Define forwards like portforwarding
    TODO: docu!
    """
    short_description="Define forwardings from instance to host"

    ctype = "forward"
    required_attributes = []
    default_attributes = []

    requires = []

    def forwards_for(self, instance):
        forwards = self.each_attribute("forward_for", args={"instance": instance})
        import pdb; pdb.set_trace()
        return flatten(forwards)

    def spawn(self):
        self.each_attribute("spawn")

    def destroy(self):
        self.each_attribute("destroy")
