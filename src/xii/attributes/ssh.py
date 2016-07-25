import os

from xii import attribute, error, guest_util
from xii.attribute import Key
from xii.output import info, show_setting, warn


class SSHAttribute(attribute.Attribute):
    name = "ssh"
    allowed_components = "node"
    requires = ["image", "user"]
    defaults = None

    keys = {'copy-key': {
                'type': Key.Dict,
                'keys': {
                    'ssh-keys': {
                        'type': Key.Array,
                        'keys': Key.String
                        },
                    'users': {
                        'required': True,
                        'type': Key.Array,
                        'keys': Key.String
                        }
                    }
                },
            'distribute-keys': {
                'type': Key.Dict,
                'keys': {
                    'ssh-keys': {
                        'type': Key.Dict,
                        'keys': Key.String
                        },
                    'domains': {
                        'required': True,
                        'type': Key.Array,
                        'keys': Key.String
                    }
                }
            }
        }

    def __init__(self, value, cmpnt):
        attribute.Attribute.__init__(self, value, cmpnt)

    def info(self):
        if not self.settings:
            return

        copy_key = self.setting('copy-key')
        if copy_key:
            show_setting('copy keys', ", ".join(copy_key['users']))

    def spawn(self, domain_name):
        if not self.settings:
            return

        guest = self.conn().guest(self.cmpnt.attribute('image').clone(domain_name))

        copy_key = self.setting('copy-key')
        if copy_key:
            info("Copy key to domains")
            self._add_keys_to_domain(guest, copy_key, domain_name)

    def _add_keys_to_domain(self, guest, copy_key, domain_name):
        keys = self._get_public_keys()
        users = guest_util.get_users(guest)

        for target in copy_key['users']:
            if target not in users:
                warn("Try to add ssh key to not existing user {}. Ignoring!".format(target))
                continue

            user = users[target]
            ssh_dir = os.path.join(user['home'], ".ssh")

            if not guest.is_dir(ssh_dir):
                guest.mkdir(ssh_dir)
                guest.chown(user['uid'], user['gid'], ssh_dir)

            authorized_file = os.path.join(ssh_dir, "authorized_keys")
            info("local => {}/{}".format(domain_name, target), 2)
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


attribute.Register.register("ssh", SSHAttribute)
