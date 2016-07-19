import os

from xii import attribute, error
from xii.attribute import Key
from xii.output import info, show_setting, warn


class SSHAttribute(attribute.Attribute):
    name = "ssh"
    allowed_components = "node"
    defaults = None

    keys = {'copy-key': {
                'type': Key.Dict,
                'keys': {
                    'ssh-key': {'type': Key.String},
                    'domains': {
                        'required': True,
                        'type': Key.Array,
                        'keys': Key.String
                        }
                    }
                },
            'distribute-keys': {
                'type': Key.Array,
                'keys': Key.String
                }
            }

    def __init__(self, value, cmpnt):
        attribute.Attribute.__init__(self, value, cmpnt)

    def info(self):
        if not self.value:
            return

        copy_key = self.setting('copy-key')
        if copy_key:
            show_setting('copy keys to host', ", ".join(copy_key['domains']))

    def spawn(self, domain_name):
        if not self.value:
            return

        guest = self.conn().guest(self.cmpnt.attribute('image').clone(domain_name))

        copy_key = self.setting('copy-key')
        if copy_key:
            info("Copy key to domains")
            self._add_keys_to_domain(guest, copy_key, domain_name)

    def _add_keys_to_domain(self, guest, copy_key, domain_name):
        key = self._get_public_key()
        passwd = self._parse_passwd(guest.cat("/etc/passwd").split("\n"))

        for user in copy_key['domains']:
            if user not in passwd:
                warn("Try to add ssh key to not existing user {}. Ignoring!".format(user))
                continue
            ssh_dir = os.path.join(passwd[user], ".ssh")

            if not guest.is_dir(ssh_dir):
                guest.mkdir(ssh_dir)

            authorized_file = os.path.join(ssh_dir, "authorized_keys")
            info("local => {}/{}".format(domain_name, user), 2)
            guest.write_append(authorized_file, key)

    def _get_public_key(self):
        if 'public-key' in self.value:
            return self.value['public-key']

        home = os.path.expanduser('~')
        pub_key = os.path.join(home, '.ssh/id_rsa.pub')
        if not os.path.isfile(pub_key):
            raise error.DoesNotExist("Could not find public key "
                                        "(search file: {})".format(pub_key))

        with open(pub_key, 'r') as hdl:
            key = hdl.read()

        return key

    def _parse_passwd(self, passwd):
        parsed = {}
        for line in passwd:
            split = line.split(":")
            if len(split) != 7:
                continue
            parsed[split[0]] = split[-2]
        return parsed


attribute.Register.register("ssh", SSHAttribute)
