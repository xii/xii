import os
import argparse
import libvirt
import subprocess
import time

from xii import definition, command, error
from xii.output import HasOutput
from xii.entity import Entity


class SSHCommand(command.Command):
    name = ['ssh']
    help = "connect to a domain"

    def run(self):
        domain_name, user = self._parse_command()

        if domain_name is None:
            nodes = self.get("components/node")
            if nodes is None:
                raise error.NotFound("Could not find domain. Maybe not started?")
            domain_name = nodes.keys()[0]

        cmpnt = self.get_component(domain_name)
        if not cmpnt:
            raise error.NotFound("Could not find `{}`. Maybe wrong directory?"
                                 .format(domain_name))

        domain = cmpnt.get_domain(domain_name)

        if not domain or not domain.isActive():
            raise error.NotFound("{} has not been started. Forgot to run "
                                 "`xii start` first?".format(domain_name))

        if user is None:
            user_attr = cmpnt.get_attribute("user")
            if user_attr is None:
                raise error.ConnError("Could not connection to {}. You did not "
                                      "specifiy any user name."
                                      .format(domain_name))
            user = user_attr.get_default_user()

        ip = cmpnt.domain_get_ip(domain_name)

        null = open(os.devnull, 'w')

        # scan key first
        subprocess.call("ssh-keygen -R {}".format(ip), shell=True, stdout=null, stderr=null)
        subprocess.call("ssh-keyscan -H {} >> ~/.ssh/known_hosts".format(ip),
                        shell=True,
                        stdout=null,
                        stderr=null)

        options = "-o HostKeyAlgorithms=ssh-rsa"
        #options = ""
        self._run_ssh_cmd(domain_name, user, ip, options, self.get("global/retry_ssh", 10))

    def _run_ssh_cmd(self, domain_name, user, ip, options="", retry=10, step=0):
        if step == retry:
            raise error.ConnError("Could not connect to {}".format(domain_name))

        self.counted(step, "connecting to {}...".format(domain_name))
        cmd = "ssh {} {}@{}".format(options, user, ip)

        #FIXME: Is there a better way to find out if a ssh connection was successfully
        #       established?
        status = subprocess.call(cmd, shell=True)
        if status == 255:
            self.counted(step, "connection refused! Retrying...")
            time.sleep(self.get("global/wait", 3))
            self._run_ssh_cmd(domain_name, user, ip, options, retry, step+1)
            
    
    def _parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("domain", nargs="?", default=None,
                            help="Name of the domain you want to connect")
        parser.add_argument("user", nargs="?", default=None,
                            help="Name of the user you want to connect")
        parser.add_argument("--port", default=None,
                            help="Port where the ssh daemon listens to")

        args = parser.parse_args(self.args())

        return args.domain, args.user



command.Register.register(SSHCommand)
