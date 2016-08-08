import os
import urllib2
import errno
import re
import socket
import time
import functools
import stat

from xii import connection, error
from xii.output import progress, warn, info

import paramiko


BUF_SIZE = 16 * 1024

import pdb;

class Ssh(connection.Connection):

    def __init__(self, url):
        Connection.__init__(self)
        self.ssh_conn = None
        self.username = None
        self.host = None
        self.url = url

        self.client = None
        self.sftp_client = None

        self._parse_url(url)

    def ssh(self, timeout=5):
        if self.client:
            return self.client

        conn_args = {'hostname': self.host}

        if self.user:
            conn_args['user'] = self.username
        
        for i in range(timeout):
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(self.host, username=self.username)
                return self.client
            except paramiko.AuthenticationException:
                raise error.ConnError("Could not connect to {} failed: "
                                     "Authentication failed".format(self.host))
            except paramiko.BadHostKeyException:
                raise error.ConnError("Could not connect to {} failed: "
                                     "Bad host key".format(self.host))

            except socket.error as err:
                warn("Connection to {}: socket error: {}".format(self.host, err))
                pass

            time.sleep(2)

        raise error.SSHError("Coult not connect to {}. Timeout!")

    def sftp(self):

        if self.sftp_client:
            return self.sftp_client

        self.sftp_client = self.ssh().open_sftp()

        return self.sftp_client

    def mkdir(self, directory, recursive=False):
        paths = [directory]
        
        if recursive:
            dirs = directory.split("/")
            curr = "/"
            paths = []
            for d in dirs:
                curr = os.path.join(curr, d)
                paths.append(curr)

        for path in paths:
            if not self.exists(path):
                self.sftp().mkdir(path)
                    
    def exists(self, path):
        try:
            self.sftp().stat(path)
        except IOError, e:
            if e[0] == 2:
                return False
            raise        
        return True

    def user(self):
        return self._shell("whoami")
        
    def user_home(self):
        return self._shell("echo $HOME")

    def copy(self, msg, source, dest):
        info(msg)
        _, stdout, _ = self.ssh().exec_command("cp {} {}".format(source, dest))
        while not stdout.channel.eof_received:
            time.sleep(1)

    def put(self, msg, source, dest):
        cb = functools.partial(progress, msg)
        self.sftp().put(source, dest, callback=cb)

    def get(self, msg, source, dest):
        cb = functools.partial(progress, msg)
        self.sftp().get(source, dest, callback=cb)

    def remove(self, path):
        if self.exists(path):
            stats = self.sftp().stat(path)
            if stat.S_ISDIR(stats.st_mode):
                self.sftp().rmdir(path)
            else:
                self.sftp().unlink(path)

    def download(self, msg, source, dest):

        progress(msg, 0, 100)
        command = "wget --progress=dot {} -O {} 2>&1 | grep --color=none -o \"[0-9]\+%\"".format(source, dest)
        _, stdout, _ = self.ssh().exec_command(command)

        for line in stdout:
            perc = int(line.replace("%", "").strip())
            progress(msg, perc, 100)

    def chmod(self, path, new_mode, append=False):
        if append:
            new_mode = self.sftp().stat(path).st_mode | new_mode
        self.sftp().chmod(path, new_mode)

    def chown(self, path, uid, gid):
        self.sftp().chown(path, uid, gid)

    def _parse_url(self, url):
        matcher = re.compile(r"qemu\+ssh:\/\/((.+)@)?(((.+)\.(.+))|(.+))\/system")
        matched = matcher.match(url)
        if not matched:
            raise error.ConnError("[io] Invalid connection URL specified.")

        self.host = matched.group(3)
        
        if matched.group(2):
            self.username = matched.group(2)

    def _shell(self, command, timeout=None, multiline=False):
        _, out, _ = self.ssh().exec_command(command, timeout=timeout)
        if not out:
            raise error.ExecError("Could not execute remote command "
                                 "`{}`".format(command))

        if multiline:
            tmp = []
            for line in out:
                tmp.append(line.strip())
            return tmp
        return out.read().strip()
