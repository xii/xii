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
        def _create_connection():
            url = self.get_virt_url()

            if not url:
                raise error.ConnError("[io] No connection url supplied")

            if url.startswith('qemu+ssh'):
                return Ssh(url)
            if url.startswith('qemu'):
                return Local()

            raise error.ConnError("Unsupported connection type. Currently "
                                  "qemu and qemu+ssh is supported")

        def _finalize_connection(connection):
            connection.finalize()

        return self.share("io", creator=_create_connection, finalizer=_finalize_connection)
