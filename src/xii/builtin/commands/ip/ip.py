import os
import argparse
import libvirt
import subprocess
import time

from xii import definition, command, error
from xii.need import NeedLibvirt, NeedSSH


class IpCommand(command.Command, NeedLibvirt):
    """Get the current ip address of a node

    Using the `--quiet` switch to fetch the ip address for scripts

    ::

        $ xii ip --quiet test-vm
        192.168.120.33

    When called directly after starting a node no ip address is assigned and
    nothing can be printed.
    """
    name = ['ip']
    help = "get ip address from host"

    @classmethod
    def argument_parser(cls):
        parser = command.Command.argument_parser(cls.name[0])
        parser.add_argument("--quiet", action="store_true", default=False,
                            help="Only output the ip or nothing if requesting failed")
        parser.add_argument("domain", nargs="?", default=None,
                            help="Name of the domain you want to connect")
        return parser

    def domain_name(self):
        if self.args().domain is not None:
            return self.args().domain

        nodes = self.get("components/node")
        if nodes is None:
            raise error.NotFound("This definition does not define any "
                                 "nodes. Checkout your definition file")

        # return the first node in the definition
        return nodes.keys()[0]

    def run(self):
        is_quiet = self.args().quiet
        domain_name = self.domain_name()

        cmpnt = self.get_component(domain_name)
        if not cmpnt:
            raise error.Bug("Could not find `{}`.".format(domain_name))
        ip = cmpnt.domain_get_ip(domain_name, quiet=is_quiet)
        print(ip)
