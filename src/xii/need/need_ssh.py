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
        """returns the default ssh connection
        Returns a _Ssh object by using the default logins
        given from the definition file. (The default user defined or 'xii')

        Returns:
            A initialized and connected _Ssh object
        """
        (user, host, password, key) = self.default_ssh_connection()
        if not user or not host:
            raise error.ConnError("Could not connect to ssh. "
                                  "Invalid configuration")

        return self.ssh(user, host, password, key)

    def ssh(self, host, user, password=None, keyfile=None):
        """creates a ssh connection to a host

        Args:
            host: host to connect to
            user: username to login
            password: plaintext password string
            keyfile: ssh key file

        Returns:
            A initialize and connected _Ssh object
        """
        connection_hash = self._generate_hash(host, user)

        retry = self.config("ssh/ssh_retry", 20)
        wait = self.config("ssh/wait", 3)

        def _create_ssh_conn():
            ssh = Ssh(self, host, user, retry, wait, password, keyfile)
            return ssh

        def _close_ssh_conn(ssh):
            ssh.close()

        return self.share(connection_hash, _create_ssh_conn, _close_ssh_conn)

    def _generate_hash(self, host, user):
        return "ssh" + md5.new("{}-{}".format(host, user)).hexdigest()
