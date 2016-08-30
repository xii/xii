import os
import re
import socket
import stat
from time import sleep

from xii import connection, error
from xii.ui import HasOutput

import paramiko


BUF_SIZE = 16 * 1024


class Ssh(connection.Connection, HasOutput):

    def __init__(self, entity, user, host, retry, wait):
        connection.Connection.__init__(self)

        self._user = user
        self._host = host

        self._retry = retry
        self._wait = wait
        self._entity = entity

        self._ssh = None
        self._sftp = None

    def get_full_name(self):
        return self._entity.get_full_name() + ["ssh"]

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

    def mkdir(self, directory):
        segments = filter(None, directory.split("/"))
        path = ""
        for seg in segments:
            path += "/" + seg
            if not self.exists(path):
                self.sftp().mkdir(path)

    def exists(self, path):
        try:
            self.sftp().stat(path)
        except IOError as e:
            if e[0] == 2:
                return False
            raise
        return True

    def user(self):
        return self.shell("whoami")

    def user_home(self):
        return self.shell("echo $HOME")

    def copy(self, msg, source, dest):
        _, stdout, _ = self.ssh().exec_command("cp {} {}".format(source, dest))
        while not stdout.channel.eof_received:
            sleep(1)

    def put(self, msg, source, dest):
        self.sftp().put(source, dest)

    def get(self, msg, source, dest):
        self.sftp().get(source, dest)

    def remove(self, path):
        if self.exists(path):
            stats = self.sftp().stat(path)
            if stat.S_ISDIR(stats.st_mode):
                self.sftp().rmdir(path)
            else:
                self.sftp().unlink(path)

    def download(self, msg, source, dest):
        command = "wget --progress=dot {} -O {} 2>&1 | grep --color=none -o \"[0-9]\+%\"".format(source, dest)
        _, stdout, _ = self.ssh().exec_command(command)

        for line in stdout:
            perc = int(line.replace("%", "").strip())

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

    @classmethod
    def parse_url(cls, url):
        matcher = re.compile(r"qemu\+ssh:\/\/((.+)@)?(((.+)\.(.+))|(.+))\/system")
        matched = matcher.match(url)
        user = None

        if not matched:
            raise error.ConnError("[io] Invalid connection URL specified.")

        host = matched.group(3)

        if matched.group(2):
            user = matched.group(2)

        return (user, host)

    @classmethod
    def new_from_url(cls, url):
        (host, user) = cls.parse_url(url)
        return cls(host, user, password=None)
