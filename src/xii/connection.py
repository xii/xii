import os
import random
import string
from stat import S_IRWXU

from abc import ABCMeta, abstractmethod


class Connection():
    __metaclass__ = ABCMeta

    def finalize(self):
        pass

    @abstractmethod
    def open(self, path, mode):
        pass

    @abstractmethod
    def mkdir(self, directory, recursive=False):
        pass

    @abstractmethod
    def stat(self, path):
        pass

    @abstractmethod
    def which(self, executable):
        pass

    @abstractmethod
    def exists(self, path):
        pass

    @abstractmethod
    def user(self):
        pass

    @abstractmethod
    def user_home(self):
        pass

    @abstractmethod
    def copy(self, msg, source, dest):
        pass

    @abstractmethod
    def download(self, msg, source, dest):
        pass

    @abstractmethod
    def chmod(self, path, new_mode, append=False):
        pass

    @abstractmethod
    def chown(self, path, uid=None, guid=None):
        pass

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def rm(self, path):
        pass

    @abstractmethod
    def get_groups(self):
        pass

    def ensure_path_exists(self, path):
        if self.exists(path):
            return

        self.mkdir(path, recursive=True)
        self.chmod(path, S_IRWXU)

    def mktempdir(self, prefix):
        user = self.user()
        users = self.get_users()
        group = self.get_groups()

        suffix = ''.join(random.choice(string.lowercase) for i in range(8))
        path = os.path.join("/var/tmp", prefix + "-" + suffix)

        self.mkdir(path)
        self.chmod(path, S_IRWXU)

        return path
