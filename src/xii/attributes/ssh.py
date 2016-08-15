import os

from Crypto.PublicKey import RSA

from xii import util
from xii.attributes.nodeattribute import NodeAttribute
from xii.need import NeedGuestFS
from xii.validator import Dict, List, String, Required, Key, Bool


class SSHAttribute(NodeAttribute, NeedGuestFS):
    entity = "ssh"

    requires = ["image", "user"]
    defaults = None

    keys = Dict([
        Key('copy-key', Dict([
            Key('ssh-keys', List(String())),
            Required(Key('users', List(String())))
        ])),
        Key('distribute-keys', Dict([
            Required(Key('users', List(String()))),
            Key('hosts', List(String())),
            Key('same-hosts', Bool())
        ]))
    ])

    def spawn(self):
        if not self.settings:
            return

        guest = self.guest()

        copy_key = self.setting('copy-key')
        if copy_key:
            self._add_keys_to_domain(guest, copy_key)


    def _add_keys_to_domain(self, guest, copy_key):
        keys = self._get_public_keys()
        users = self.guest_get_users()

        for target in copy_key['users']:
            if target not in users:
                self.warn("try to add ssh key to not existing user {}. Ignoring!".format(target))
                continue

            user = users[target]
            user_ssh_dir = os.path.join(user['home'], ".ssh")
            authorized_file = os.path.join(user_ssh_dir, "authorized_keys")

            self.say("local keys => {}".format(target))

            if not guest.is_dir(user_ssh_dir):
                guest.mkdir(user_ssh_dir)
                guest.chown(user['uid'], user['gid'], user_ssh_dir)

            guest.write_append(authorized_file, "".join(keys))
            guest.chown(user['uid'], user['gid'], authorized_file)

            # FIXME: Find better way to deal with selinux labels
            if guest.get_selinux():
                guest.sh("chcon -R unconfined_u:object_r:user_home_t:s0 {}".format(user_ssh_dir))

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

    def _distribute_keys(self):
        hosts = self.settings("distribute-keys/hosts")
        users = self.settings("distribute-keys/users")
        same_host = self.settings("distribute-keys/same-hosts", False)

        guest_users = self.guest_get_users()

        # check if user wants current host to distribute his ssh keys
        if hosts and self.component_name() not in hosts:
            return

        keys = self.global_share("ssh_distribute_keys", default={})

        for user in users:
            if user not in guest_users:
                self.warn("distribute key failed: user {} does "
                          "not exist".format(user))
                continue

        print("add keys but nope...")


SSHAttribute.register()
