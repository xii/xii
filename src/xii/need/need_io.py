from abc import ABCMeta, abstractmethod

from xii import error
from xii.connections.local import Local
from xii.connections.ssh import Ssh


class NeedIO():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_virt_url(self):
        pass

    def io(self):
        """get a io object to the local or remote host
        Will return a local connection object in case of a local connection
        used or a remote ssh/sftp connection if the host is remote.

        Returns:
            A connection object
        """
        def _create_connection():
            url = self.get_virt_url()
            self.verbose("connection url = {}".format(url))

            if not url:
                raise error.ConnError("[io] No connection url supplied")

            if url.startswith('qemu+ssh'):
                retry = self.config("ssh/ssh_retry", 20)
                wait = self.config("ssh/wait", 3)
                return Ssh.new_from_url(self, url, retry, wait)
            if url.startswith('qemu'):
                return Local()

            raise error.ConnError("Unsupported connection type. Currently "
                                  "qemu and qemu+ssh is supported")

        def _finalize_connection(connection):
            connection.finalize()

        return self.share("io", creator=_create_connection) #finalizer=_finalize_connection)
