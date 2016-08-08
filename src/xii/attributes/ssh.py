import os

from xii import util
from xii.attribute import Attribute
from xii.validator import Dict, List, String, Required, Key


class SSHAttribute(Attribute):
    entity = "ssh"
    needs = ["node"]

    requires = ["image", "user"]
    defaults = None

    keys = Dict([
        Key('copy-key', Dict([
            Key('ssh-keys', List(String())),
            Required(Key('users', List(String())))
        ]))
    ])

    def __init__(self, value, cmpnt):
        Attribute.__init__(self, value, cmpnt)

    def prepare(self):
        if not self.settings:
            return

        copy_key = self.setting('copy-key')
        if copy_key:
            self.add_info('copy keys', ", ".join(copy_key['users']))

    def spawn(self):
        if not self.settings:
            return

        guest = self.conn().guest(self.cmpnt.attribute('image').image_path())

        copy_key = self.setting('copy-key')
        if copy_key:
            self.say("copy key to domains")
            self._add_keys_to_domain(guest, copy_key)

    def _add_keys_to_domain(self, guest, copy_key):
        keys = self._get_public_keys()
        users = util.get_users(guest)

        for target in copy_key['users']:
            if target not in users:
                self.warn("try to add ssh key to not existing user {}. Ignoring!".format(target))
                continue

            self.add("adding key to {}".format(target))
            user = users[target]
            ssh_dir = os.path.join(user['home'], ".ssh")

            if not guest.is_dir(ssh_dir):
                guest.mkdir(ssh_dir)
                guest.chown(user['uid'], user['gid'], ssh_dir)

            authorized_file = os.path.join(ssh_dir, "authorized_keys")
            guest.write_append(authorized_file, "".join(keys))
            guest.chown(user['uid'], user['gid'], authorized_file)

            # FIXME: Find better way to deal with selinux labels
            if guest.get_selinux():
                guest.sh("chcon -R unconfined_u:object_r:user_home_t:s0 {}".format(ssh_dir))


    def _get_public_keys(self):
        ssh_keys = self.setting('copy-key/ssh-keys')
        if ssh_keys:
            return ssh_keys

        # fetch keys from local user
        ssh_keys = []
        home = os.path.expanduser('~')

        pub_keys = [os.path.join(home, '.ssh/id_rsa.pub'),
                    os.path.join(home, '.ssh/id_ecdsa.pub')]

        for key_path in pub_keys:
            if os.path.isfile(key_path):
                with open(key_path, 'r') as hdl:
                    ssh_keys.append(hdl.read())
        return ssh_keys

    def _parse_passwd(self, passwd):
        parsed = {}
        for line in passwd:
            split = line.split(":")
            if len(split) != 7:
                continue
            parsed[split[0]] = split[-2]
        return parsed


SSHAttribute.register()
