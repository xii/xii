import os
import argparse
import libvirt
import subprocess

from xii import definition, command, components, error


class SSHCommand(command.Command):
    name = ['ssh']
    help = "connect to a domain"

    def run(self):

        dfn_path, domain_name, user = self._parse_command()

        dfn = definition.from_file(dfn_path, self.config)

        runtime = {
                'definition': dfn,
                'config': self.config,
                'userinterface': self.userinterface
        }

        cmpnt = components.get(domain_name, runtime)
        domain = cmpnt.get_domain(domain_name)

        if not user:
            user = cmpnt.attribute("user").get_default_user()

        if not domain or not cmpnt:
            raise error.NotFound("Could not find {}".format(domain_name))

        if not domain.isActive():
            self.userinterface.warn("{} is not running. Try starting the domain first".format(domain_name))
            return

        # Currently there is no way to determine net name (like vnet0) from a networkname
        # eg. default -> vibr0 -> ??? -> vnet0

        nets = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)

        if not len(nets):
            raise error.ExecError("Could not fetch ip address for ssh connection")

        net = nets.itervalues().next()

        if not len(net['addrs']):
            raise error.ExecError("No ip address was accociated with {}".format(domain_name))

        ip = net['addrs'][0]['addr']

        null = open(os.devnull, 'w')

        # scan key first
        subprocess.call("ssh-keygen -R {}".format(ip), shell=True, stdout=null, stderr=null)
        subprocess.call("ssh-keyscan -H {} >> ~/.ssh/known_hosts".format(ip),
                        shell=True,
                        stdout=null,
                        stderr=null)

        # options = "-o HostKeyAlgorithms=ssh-rsa"
        options = ""
        cmd = "ssh {} {}@{}".format(options, user, ip)
        subprocess.call(cmd, shell=True)

    def _parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("domain",
                            help="Name of the domain you want to connect")
        parser.add_argument("user", nargs="?", default=None,
                            help="Name of the user you want to connect")
        parser.add_argument("--port", default=None,
                            help="Port where the ssh daemon listens to")
        parser.add_argument("definition", nargs="?", default=None,
                            help="File to xii definition")

        args = parser.parse_args(self.args)

        return args.definition, args.domain, args.user


command.Register.register(SSHCommand)
