import subprocess
import paramiko
import pytest

from time import sleep


def new_ssh(domain, user=None):
    pass


class SSH():
    def __init__(domain, user):
        self._domain = domain
        self._user   = user

    def run(command):
        pass

    def file_contains(path):
        pass

    def exists(path):
        pass

    def connect(key=None, password=None):
        if self._ssh:
            return self._ssh

        host = self._find_host()

        for _ in range(20):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=self._user)
                self._ssh = client
                return self._ssh

            except (paramiko.BadHostKeyException,
                    paramiko.AuthenticationException,
                    paramiko.SSHException,
                    socket.error) as e:
                sleep(2)
        pytest.xfail("ssh connect failed: Could not connect to host `{}`".format(host))

    def sftp(self):
        if self._sftp:
            return self._sftp

        self._sftp = self._ssh.open_sftp()
        return self._sftp

    def _find_host():
        process = subprocess.call(["xii", "ip", "--quiet", domain])
        ip = process.stdout.read()
        

