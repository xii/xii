import os

from xii import attribute, paths, error
from xii.output import info, show_setting


class SSHAttribute(attribute.Attribute):
    name = "ssh"
    allowed_components = "node"
    defaults = None

    def __init__(self, value, cmpnt):
        attribute.Attribute.__init__(self, value, cmpnt)

    def info(self):
        if not self.value:
            return

        if 'copy-key' in self.value:
            show_setting('distribute pub key', ", ".join(self.value['copy-key']))


    def spawn(self, domain_name):
        if not self.value:
            return

        guest = self.conn().guest(self.cmpnt.attribute('image').clone(domain_name))

        if 'copy-key' in self.value:
            info("Distributing public keys")
            self._add_keys_to_domain(guest, domain_name)

    def _add_keys_to_domain(self, guest, domain_name):
        key = self._get_public_key()
        passwd = self._parse_passwd(guest.cat("/etc/passwd").split("\n"))

        for user in self.value['copy-key']:
            if user not in passwd:
                warn("Try to add ssh key to not existing user {}. Ignoring!".format(user))
                continue
            ssh_dir = os.path.join(passwd[user], ".ssh")

            if not guest.is_dir(ssh_dir):
                guest.mkdir(ssh_dir)

            authorized_file = os.path.join(ssh_dir, "authorized_keys")
            info("local => {}/{}".format(domain_name, user), 2)
            guest.write_append(authorized_file, key)

        import pdb; pdb.set_trace()

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
