import os

from xii.components.ansible import AnsibleAttribute
from xii.validator import List, String, Dict, VariableKeys, Or
from xii.need import NeedLibvirt, NeedIO, NeedSSH
from xii import util


class HostsAttribute(AnsibleAttribute, NeedLibvirt, NeedIO, NeedSSH):
    """
    The ansible hosts defines how the ansible inventory is populated.

    To simply define all in one group you can use a list of hosts which should
    be added.

    Example:
    ::
      privision-vms:
        type: ansible
        hosts: [ vm-1, vm-2, vm-5 ]

    Or if you need more than one group you can define multiple groups:
    ::
      privision-vms:
        type: ansible
        hosts:
            first-group: [ vm-1, vm-2 ]
            second-group: [ vm-3, vm-4 ]

    .. note::

        You can use also use the basename of a node. For example if you define:
        ::

            test-vms:
                type: node
                image: {{ image }}
                count: 4

        You can use:
        ::

            hosts: [ test-vms ]

        to match all nodes at once
    """

    example = """
    vm:
      type: node
      pool: default
      network: default
      image: {{ image }}
      count: 6

    provision-it:
        type: ansible
        hosts:
            basic-config: [ vm ]
            webservers: [ vm-1, vm-2, vm-3 ]
            db: [ vm-4 ]
            haproxy: [ vm-5, vm-6 ]
    """

    atype = "hosts"
    defaults = None
    keys = Or([
        List(String("hosts")),
        Dict([VariableKeys(List(String("hosts")), example="hostname")])
    ])

    def _fetch_ips(self, hosts):
        def _to_tuple(host):
            return (host, self.domain_get_ip(host, quiet=True))
        return util.in_parallel(3, hosts, _to_tuple)

    def _check_ssh_servers(self, hosts):
        def _check_ssh(host, ip):
            if self.ssh_host_alive(ip):
                return (host, ip)
            return None
        return filter(None, util.in_parallel(3, hosts, lambda x: _check_ssh(*x)))

    def generate_inventory(self, tmp):
        known_hosts = {}
        hosts       = self._get_hosts()
        inventory   = os.path.join(tmp,"inventory")
        to_write    = []
        all_hosts   = []

        # fetch all hostnames
        map(all_hosts.extend, self._get_hosts().values())
        all_hosts = list(set(all_hosts))

        # fetch ips and check ssh connectifity
        ips = self._fetch_ips(all_hosts)
        ips = self._check_ssh_servers(ips)

        for group, hosts in self._get_hosts().items():
            to_write.append("[{}]".format(group))

            for host in hosts:
                self.say("Waiting for {} to get a IP address...".format(host))
                ip = self.domain_get_ip(host, verbose=self.is_verbose())

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
