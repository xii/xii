import os
import md5
import paramiko
import socket

from time import sleep

from xii import error
from xii.ui import HasOutput


class NeedSSH(HasOutput):
    def get_default_user(self):
        return None

    def get_default_host(self):
        return None

    def get_default_password(self):
        return None

    def run_default_ssh(self, command):
        user = self.get_default_user()
        host = self.get_default_host()
        pw = self.get_default_password()

        if not user or not host:
            self.warn("Invalid user/host configuration")
            return False

        self.run_ssh(host, user, command, pw)

    def copy_default_to_tmp(self, source):
        user = self.get_default_user()
        host = self.get_default_host()
        pw = self.get_default_password()

        if not user or not host:
            self.warn("Invalid user/host configuration")
            return False
        return self.copy_to_tmp(host, user, pw, source)

    def run_ssh(self, host, user, command, password=None):
        conn = self.ssh(host, user, password)

        chan = conn.get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)
        stdout = chan.makefile('r', -1)

        for line in stdout:
            self.say(line.strip())

        return chan.recv_exit_status()

    def copy_to_tmp(self, host, user, password, source):
        tmp_dir = "/tmp/xii"
        conn = self.ssh(host, user, password)
        name = os.path.basename(source)
        dest = os.path.join(tmp_dir, name)

        sftp = conn.open_sftp()

        # check if tmp_dir exists
        try:
            sftp.stat(tmp_dir)
        except IOError as e:
            if e[0] == 2:
                sftp.mkdir(tmp_dir)

        sftp.put(source, dest)
        return dest

    def ssh(self, host, user, password=None):
        connection_hash = self._generate_hash(host, user)

        def _create_ssh_conn():
            for i in range(self.get_config().retry("ssh")):
                self.counted(i, "Connection to host...")
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(host, username=user)
                    return client

                except (paramiko.BadHostKeyException,
                        paramiko.AuthenticationException,
                        paramiko.SSHException,
                        socket.error) as e:
                    sleep(self.get_config().wait())

            raise error.ConnError("Could not connect to {}@{}. Giving up!"
                                  .format(user, host))

        def _close_ssh_conn(conn):
            conn.close()
        return self.share(connection_hash, _create_ssh_conn, _close_ssh_conn)

    def _generate_hash(self, host, user):
        return "ssh" + md5.new("{}-{}".format(host, user)).hexdigest()
