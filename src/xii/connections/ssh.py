import os
import socket
import stat
import string
import random
from time import sleep

from xii import connection, error, util
from xii.output import HasOutput

import paramiko


BUF_SIZE = 16 * 1024


class Ssh(connection.Connection, HasOutput):

    def __init__(self, entity, user, host, retry, wait, password=None, keyfile=None):
        connection.Connection.__init__(self)

        #TODO: Add password and key support
        self._user = user
        self._host = host

        self._retry = retry
        self._wait = wait
        self._entity = entity

        self._ssh = None
        self._sftp = None

    def entity_path(self):
        return self._entity.entity_path() + ["ssh"]

    def ssh(self):
        if self._ssh:
            return self._ssh

        for i in range(self._retry):
            self.counted(i, "connecting to host {}...".format(self._host))
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(self._host, username=self._user)
                self._ssh = client
                sleep(self._wait)
                self.say("connected!")
                return self._ssh

            except (paramiko.BadHostKeyException,
                    paramiko.AuthenticationException,
                    paramiko.SSHException,
                    socket.error) as e:
                sleep(self._wait)

        raise error.ConnError("Could not connect to {}@{}. Giving up!"
                                .format(self._user, self._host))

    def sftp(self):
        if self._sftp:
            return self._sftp

        self._sftp = self.ssh().open_sftp()
        return self._sftp

    def open(self, path, mode):
        return self.sftp().open(path)

    def mkdir(self, directory):
        segments = filter(None, directory.split("/"))
        path = ""
        for seg in segments:
            path += "/" + seg
            if not self.exists(path):
                self.sftp().mkdir(path)

    def stat(self, path):
        return self.sftp().stat(path)

    def which(self, executable):
        # FIXME: Potential dangerous. Add a more advanced solution
        result = self.shell("which {}".format(executable))
        if os.path.isabs(result):
            return result
        return None

    def exists(self, path):
        try:
            self.stat(path)
        except IOError as e:
            if e[0] == 2:
                return False
            raise
        return True

    def rm(self, path):
        files = self.sftp().listdir(path)
        for file_ in files:
            to_remove = os.path.join(path, file_)
            try:
                self.sftp().remove(to_remove)
            except IOError:
                self.rm(to_remove)
        self.sftp().remove(path)

    def user(self):
        return self.shell("whoami")

    def user_home(self):
        return self.shell("echo $HOME")

    def copy(self, source, dest):
        chan = self.ssh().get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command("cp {} {}".format(source, dest))
        return chan.recv_exit_status() == 0

    def upload(self, source, dest):
        try:
            self.sftp().put(source, dest)
        except IOError, SSHException:
            return False
        return True

    def download(self, source, dest):
        try:
            self.sftp().get(source, dest)
        except IOError, SSHException:
            return False
        return True

    def download_url(self, url, dest):
        command = "wget --progress=dot {} -O {}".format(source, dest)
        chan = self.ssh().get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)
        return chan.recv_exit_status() == 0

    def chmod(self, path, new_mode, append=False):
        if append:
            new_mode = self.sftp().stat(path).st_mode | new_mode
        self.sftp().chmod(path, new_mode)

    def chown(self, path, uid, gid):
        self.sftp().chown(path, uid, gid)

    def run(self, command):
        conn = self.ssh()

        chan = conn.get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)
        stdout = chan.makefile('r', -1)

        for line in stdout:
            self.say(line.strip())

        return chan.recv_exit_status()

    def copy_to_tmp(self, source):
        tmp_dir = "/tmp/xii"
        name = os.path.basename(source)
        dest = os.path.join(tmp_dir, name)

        self.mkdir(tmp_dir)
        self.put(source, dest)
        return dest

    def close(self):
        if self._ssh:
            self._ssh.close()

    def shell(self, command, multiline=False):
        _, out, _ = self.ssh().exec_command(command)
        if multiline:
            tmp = []
            for line in out:
                tmp.append(line.strip())
            return tmp
        return out.read().strip()

    def get_users(self):
        with self.open("/etc/passwd") as source:
            return util.parse_passwd([line.rstrip('\n') for line in source])

    def get_groups(self):
        with self.open("/etc/group") as source:
            return util.parse_groups([line.rstrip('\n') for line in source])

    def call(self, command, *args):
        command = " ".join([command] + list(args))
        chan = self.ssh().get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)

        if self.is_verbose():
            for line in chan.stdout:
                self.verbose(line)
        return chan.recv_exit_status()

    @classmethod
    def parse_url(cls, url):
        matcher = re.compile(r"qemu\+ssh:\/\/((.+)@)?(((.+)\.(.+))|(.+))\/system")
        matched = matcher.match(url)
        user = None

        if not matched:
            raise error.ConnError("Invalid connection URL specified. `{}` is "
                                  "invalid!".format(url))

        host = matched.group(3)

        if matched.group(2):
            user = matched.group(2)

        return (user, host)

    @classmethod
    def new_from_url(cls, entity, url, retry, wait, key=None):
        parsed = util.parse_virt_url(url)

        if parsed is None:
            raise error.ConnError("Invalid connection URL specified. `{}` is "
                                  "invalid!".format(url))
        (user, host) = parsed
        return cls(entity, user, host, retry, wait, key)
