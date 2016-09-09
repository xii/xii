from abc import ABCMeta, abstractmethod

import guestfs

from xii import util


class NeedGuestFS():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_tmp_volume_path(self):
        pass

    def guest(self):
        def _start_guestfs():
            path = self.get_tmp_volume_path()
            print("mounting " + path)
            

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

    def guest_get_users(self):
        content = self.guest().cat('/etc/passwd').split("\n")
        return util.parse_passwd(content)

    def guest_user_home(self, name):
        users = self.guest_get_users()
        if name not in users:
            return None

        return users[name]["home"]

    def guest_get_groups(self):
        content = self.guest().cat('/etc/group').split("\n")
        return util.parse_groups(content)
