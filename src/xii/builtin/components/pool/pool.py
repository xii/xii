import libvirt

from xii.component import Component
from xii.need import NeedLibvirt
from xii import error, paths, util


class PoolComponent(Component, NeedLibvirt):
    entity = "pool"

    defaults = []
    requires = []

    xml_pool = []







#         network = self.get_network(name, raise_exception=False)

#         if not network:
#             is_created = self.get_definition().item(name,
#                                                     item_type="network")
#             if not is_created:
#                 raise error.NotFound("Could not find network ({})"
#                                      .format(name))
#             # wait for network to become ready
#             for _ in range(self.get_config().retry("network")):
#                 network = self.get_network(name, raise_exception=False)

#                 if network:
#                     return network
#                 sleep(self.get_config().wait())

#             raise error.ExecError("Network {} has not become ready in "
#                                   "time. Giving up".format(name))
#         return network
        

#     def add_xml(self, xml):
#         self.xml_net.append(xml)

#     def start(self):
#         pass

#     def destroy(self):
#         pass

PoolComponent.register()
