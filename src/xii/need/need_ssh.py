from abc import ABCMeta, abstractmethod

import md5

from xii import error
from xii.output import HasOutput
from xii.connections.ssh import Ssh


class NeedSSH(HasOutput):
    __meta__ = ABCMeta

    @abstractmethod
    def default_ssh_connection(self):
        pass

    def default_ssh(self):
        (user, host, password, key) = self.default_ssh_connection()
        if not user or not host:
            raise error.ConnError("Could not connect to ssh. "
                                  "Invalid configuration")

        return self.ssh(user, host, password, key)

    def ssh(self, host, user, password=None, keyfile=None):
        connection_hash = self._generate_hash(host, user)

        retry = self.get_config().retry("ssh", default=20)
        wait = self.get_config().wait(default=5)

        def _create_ssh_conn():
            ssh = Ssh(self, host, user, retry, wait, password, keyfile)
            return ssh

        def _close_ssh_conn(ssh):
            ssh.close()

        return self.share(connection_hash, _create_ssh_conn, _close_ssh_conn)

    def _generate_hash(self, host, user):
        return "ssh" + md5.new("{}-{}".format(host, user)).hexdigest()
