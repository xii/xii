import os
import argparse
import libvirt
import subprocess
import time

from xii import definition, command, error
from xii.need import NeedLibvirt, NeedSSH


class SSHCommand(command.Command, NeedLibvirt, NeedSSH):
    name = ['ssh']
    help = "connect to a domain"

    @classmethod
    def argument_parser(cls):
        parser = command.Command.argument_parser(cls.name[0])
        parser.add_argument("domain", nargs="?", default=None,
                            help="Name of the domain you want to connect")
        parser.add_argument("user", nargs="?", default=None,
                            help="Name of the user you want to connect")
        parser.add_argument("--port", default=None,
                            help="Port where the ssh daemon listens to")
        return parser

    def user_name(self, cmpnt):
        if self.args().user is not None:
            return self.args().user

        #FIXME: Add default user after ansible branch is merged
        attr = cmpnt.get_attribute("user")
        if attr is None:
            raise error.ConnError("Could not find default ssh user")
        return attr.default_user()

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
        domain_name = self.domain_name()

        cmpnt = self.get_component(domain_name)
        if not cmpnt:
            raise error.NotFound("Could not find `{}`. Maybe wrong directory?"
                                 .format(domain_name))

        user = self.user_name(cmpnt)
        ip = cmpnt.domain_get_ip(domain_name)
        self.say("{} has IP {}".format(domain_name, ip))
        null = open(os.devnull, 'w')
        retry = self.get("global/retry_ssh", 20)

        # scan key first
        subprocess.call("ssh-keygen -R {}".format(ip),
                        shell=True,
                        stdout=null,
                        stderr=null)

        subprocess.call("ssh-keyscan -H {} >> ~/.ssh/known_hosts".format(ip),
                        shell=True,
                        stdout=null,
                        stderr=null)

        self._run_ssh_cmd(domain_name, user, ip, retry)

    def _run_ssh_cmd(self, name, user, ip, retry, options="", step=0):
        if step == retry:
            raise error.ConnError("Could not connect to {}".format(name))

        self.counted(step, "connecting to {}...".format(name))
        cmd = "ssh {} {}@{}".format(options, user, ip)

        #FIXME: Is there a better way to find out if a ssh connection was successfully
        #       established?
        status = subprocess.call(cmd, shell=True)
        if status == 255:
            self.counted(step, "connection refused! Retrying...")
            time.sleep(self.get("global/wait", 3))
            self._run_ssh_cmd(name, user, ip, options, retry, step+1)
