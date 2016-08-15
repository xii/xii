from abc import ABCMeta, abstractmethod

import guestfs


class NeedGuestFS():
    __metaclass__ = ABCMeta

    @abstractmethod
    def share(self, name, creator, finalizer):
        pass

    @abstractmethod
    def get_domain_image_path(self):
        pass

    def guest(self):
        def _start_guestfs():
            path = self.get_domain_image_path()

            guest = guestfs.GuestFS()

            guest.add_drive(path)
            guest.launch()
            guest.mount("/dev/sda1", "/")

            if guest.exists('/etc/sysconfig/selinux'):
                guest.get_selinux = lambda: 1

            return guest

        def _close_guest(guest):
            guest.sync()
            guest.umount("/")
            guest.close()

        return self.share("guestfs", _start_guestfs, _close_guest)
