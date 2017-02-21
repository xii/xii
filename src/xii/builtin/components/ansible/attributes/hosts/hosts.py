import os

from xii.components.ansible import AnsibleAttribute
from xii.validator import List, String, Dict, VariableKeys, Or
from xii.need import NeedLibvirt, NeedIO
from xii import util


class HostsAttribute(AnsibleAttribute, NeedLibvirt, NeedIO):
    atype = "hosts"
    defaults = None
    keys = Or([
        List(String("hosts")),
        Dict([VariableKeys(List(String("hosts")), example="hostname")])
    ])

    def generate_inventory(self, tmp):
        known_hosts = {}
        hosts = self._get_hosts()
        inventory = os.path.join(tmp,"inventory")

        to_write = []

        # fetch all ip addresses
        all_hosts = []
        map(all_hosts.extend, self._get_hosts().values())
        all_hosts = list(set(all_hosts))

        status = util.in_parallel(3, all_hosts, lambda h: self.ssh_host_alive(h))
        import pdb; pdb.set_trace()


        for group, hosts in self._get_hosts().items():
            to_write.append("[{}]".format(group))

            for host in hosts:
                ip = self.domain_get_ip(host)

                cmpnt = self.get_component(host)

                if ip is None:
                    raise error.ExecError("Could not fetch all required ip "
                                        "addresses")
                entry = [
                    host,
                    "ansible_connection=ssh",
                    "ansible_port=22",
                    "ansible_host={}".format(ip),
                    "ansible_user={}".format(cmpnt.ssh_user())
                ]
                to_write.append("\t".join(entry))

        with self.io().open(inventory, "w") as inv:
            inv.write("\n".join(to_write))

        return inventory

    def _get_hosts(self):
        if self.settings() is None:
            return self._generate_hosts()

        if isinstance(self.settings(), dict):
            return self.settings()

        # a list is given
        if isinstance(self.settings(), list):
            return {"all": self.settings()}

        raise error.Bug("Can not create host list for ansible")


    def _generate_hosts(self):
        import pdb; pdb.set_trace()
