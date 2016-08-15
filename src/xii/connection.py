from abc import ABCMeta, abstractmethod


class Connection():
    __metaclass__ = ABCMeta

    def finalize(self):
        pass

    @abstractmethod
    def mkdir(self, directory, recursive=False):
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
    def remove(self, path):
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
