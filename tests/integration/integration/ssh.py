import subprocess
import socket
import paramiko
import pytest

from time import sleep

def connect_to(domain, user, pw, deffile):
    return SSH(deffile, domain, user, password=pw, keyfile=None)

def find_host_ip(domain, deffile):
    proc = subprocess.Popen(["xii", "--deffile", deffile, "ip", "--quiet", domain],
            stdout=subprocess.PIPE)
    (out, _) = proc.communicate()

    if out.startswith("[xii]"):
        pytest.fail("Could not fetch valid ip address...")
    return out

class SSH():
    def __init__(self, deffile, domain, user, password=None, keyfile=None):
        self._domain = domain
        self._user   = user
        self._def    = deffile
        self._pwd    = password
        self._key    = keyfile
        self._ssh    = None
        self._sftp   = None

    def run(self, command):
        conn = self.connect()
        chan = conn.get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)
        stdout = chan.makefile('r', -1)
        return stdout.read().strip()

    def file_contains(self, path, pattern):
        hdl = self.sftp().open(path)
        result = re.match(pattern, hdl.read())
        hdl.close()
        return result.groups()

    def stat(self, path):
        return self.sftp().stat(path)

    def exists(self, path):
        try:
            self.stat(path)
        except IOError as e:
            if e[0] == 2:
                return False
            raise
        return True

    def connect(self):
        if self._ssh:
            return self._ssh

        host = find_host_ip(self._domain, self._def)

        for _ in range(40):
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
                print("[ssh] Connecting to {}...".format(self._domain))
                sleep(5)
        pytest.fail("ssh connect failed: Could not connect to host `{}`".format(host))

    def sftp(self):
        if self._sftp:
            return self._sftp

        self._sftp = self.connect().open_sftp()
        return self._sftp

