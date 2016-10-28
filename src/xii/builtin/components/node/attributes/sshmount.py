import os
import getpass

from multiprocessing import Lock


from xii import error, util, need
from xii.validator import Dict, String, Required, Key, VariableKeys

from base import NodeAttribute


class SSHMountAttribute(NodeAttribute, need.NeedGuestFS, need.NeedSSH):
    atype = "sshmount"
    requires = ["image", "ssh", "user", "network"]

    key_path = ".ssh/xii-sshfs.key"
    lock = Lock()

    keys = Dict([
        VariableKeys(Dict([
            Required(Key("source", String())),
            Key("user", String()),
            Key("mode", String())
            ]))
        ])

    def get_default_user(self):
        return self.other_attribute("user").get_default_user()

    def get_default_host(self):
        return self.domain_get_ip(self.component_entity())

    def sshfs_key_path(self, name):
        home = self.guest_user_home(name)
        if not home:
            return None
        return os.path.join(home, self.key_path)

    def spawn(self):
        self._check_sshfs_compability()

        required = self._get_required_users()
        host = self._host_name()

        self.lock.acquire()
        authed_hosts = self._authorized_hosts()

        for user, home in required.items():
            path = os.path.join(home, self.key_path)

            sign = user + "@" + host
            (key, pubkey) = util.generate_rsa_key_pair()

            # save private key to domain_image
            self.say("{} => {}".format(user, self.component_entity()))
            self.guest().write(path, key)

            for idx, host in enumerate(authed_hosts):
                # check if public key alreay exists. If so update key
                if host.find(sign) != -1:
                    self.say("update authorized_keys ({})".format(sign))
                    authed_hosts[idx] = pubkey + " " + sign
                    break
            else:
                self.say("{} => local authorized_keys".format(sign))
                authed_hosts.append(pubkey + " " + sign)

        with open(self._authorized_keys_path(), "w") as auth:
            authed_hosts = filter(None, authed_hosts)
            auth.write("\n".join(authed_hosts))
        self.lock.release()

    def destroy(self):
        authed_hosts = self._authorized_hosts()
        host = self._host_name()

        if not os.path.exists(self._authorized_keys_path()):
            return

        # removing key from authorized_keys
        self.lock.acquire()
        for mount in self.settings().values():
            user = self.get_default_user()

            if "user" in mount:
                user = mount["user"]

            sign = user + "@" + host

            for idx, host in enumerate(authed_hosts):
                if host.find(sign) != -1:
                    del authed_hosts[idx]
                    break

        with open(self._authorized_keys_path(), "w") as auth:
            authed_hosts = filter(None, authed_hosts)
            auth.write("\n".join(authed_hosts))

        self.lock.release()

    def after_start(self):
        self._mount_dirs()
        pass

    def stop(self):
        self._umount_dirs()
        pass

    def after_resume(self):
        self._mount_dirs()
        pass

    def suspend(self):
        self._umount_dirs()
        pass

    def _mount_dirs(self):
        host = self.network_get_host_ip(self.other_attribute("network").settings)
        user = getpass.getuser()
        ssh  = self.default_ssh()
        key  = os.path.join("~", self.key_path)

        for dest, settings in self.settings().items():
            user = self.get_default_user()
            source = settings["source"]

            if not os.path.isdir(source):
                self.warn("sshfs source `{}` is not a directory"
                          .format(source))
                continue

            if "user" in settings:
                user = settings["user"]

            # make a absolute path if neccessary
            if not os.path.isabs(source):
                source = os.path.join(os.getcwd(), source)
            if not os.path.isabs(dest):
                dest = os.path.join(ssh.user_home(), dest)

            ssh.mkdir(dest)

            options = ("-o StrictHostKeyChecking=no "
                       "-o UserKnownHostsFile=/dev/null "
                       "-o IdentityFile={}".format(key))
            self.say("{} => {}".format(source, dest))

            ssh.run("sshfs {}@{}:{} {} {}".format(user, host, source, dest, options))

    def _umount_dirs(self):
        ssh  = self.default_ssh()
        for dest, settings in self.settings().items():
            if not os.path.isabs(dest):
                dest = os.path.join(ssh.user_home(), dest)
            self.say("unmounting {}...".format(dest))
            ssh.shell("fusermount -u {}".format(dest))

    def _authorized_keys_path(self):
        local_home = os.path.expanduser('~')
        return os.path.join(local_home, ".ssh/authorized_keys")

    def _authorized_hosts(self):
        authorized_keys = self._authorized_keys_path()

        # touch the file if not exists
        if not os.path.isfile(authorized_keys):
            with open(authorized_keys, "a"):
                pass

        with open(authorized_keys, "r") as auth:
            content = [line.strip() for line in auth.readlines()]
            return filter(None, content)

    def _host_name(self):
        return self.component_entity()

    def _check_sshfs_compability(self):
        sshfs_locations = ["/usr/bin/sshfs"]

        self.say("checking sshfs compability")
        for location in sshfs_locations:
            if self.guest().exists(location):
                return

        raise error.NotFound("Image for {} seems to not support sshfs."
                             .format(self.component_entity()))

    def _get_required_users(self):
        required = {}
        users = self.guest_get_users()
        default = self.other_attribute("user").get_default_user()

        for mount in self.settings().values():
            user = default

            if "user" in mount:
                user = mount["user"]

            if user not in users:
                self.warn("can not use {} for sshfs. User does not exist"
                          .format(user))
                continue

            # we already prepare this user
            if user in required:
                continue

            required[user] = users[user]["home"]
        return required


SSHMountAttribute.register()
