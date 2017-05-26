from abc import ABCMeta, abstractmethod

import md5
import paramiko
import socket
import time

from xii import error
from xii.output import HasOutput
from xii.connections.ssh import Ssh


class NeedSSH(HasOutput):
    __metaclass__ = ABCMeta

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

    def ssh_host_alive(self, host, timeout=20):
        """check if a ssh server is running

        Args:
            host: domain or IP Address to connect to
            timeout: Timeout after n retrys

        Returns:
            True if a server is running, False otherwise
        """
        retry = self.config("ssh/ssh_retry", timeout)
        wait = self.config("ssh/wait", 2)
        client = None

        self.verbose("check {} ssh's server...".format(host))
        for _ in range(retry):
            try:
                client = paramiko.SSHClient()
                client.connect(host,
                               username="xii",
                               password="xii",
                               timeout=0.2)
                return True
            except socket.error:
                time.sleep(wait)
            except (paramiko.BadHostKeyException,
                    paramiko.AuthenticationException,
                    paramiko.SSHException):
                return True
            finally:
                if client:
                    client.close()
        return False

    def _generate_hash(self, host, user):
        return "ssh" + md5.new("{}-{}".format(host, user)).hexdigest()
