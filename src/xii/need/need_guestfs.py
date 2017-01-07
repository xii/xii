from abc import ABCMeta, abstractmethod

import guestfs

from xii import util, error


class NeedGuestFS():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_tmp_volume_path(self):
        pass

    def guest(self):
        """get the guestfs handle to the current image

        Returns:
            A mounted guestfs object
        """
        def _start_guestfs():
            try:
                path = self.get_tmp_volume_path()
                guest = guestfs.GuestFS()

                guest.add_drive(path)
                guest.launch()
                guest.mount("/dev/sda1", "/")

                if guest.exists('/etc/sysconfig/selinux'):
                    guest.get_selinux = lambda: 1
            except RuntimeError as e:
                raise error.ExecError("guestfs error: {}".format(e))

            return guest

        def _close_guest(guest):
            guest.sync()
            guest.umount("/")
            guest.close()

        return self.share("guestfs", _start_guestfs, _close_guest)

    def guest_get_users(self):
        """get users from image

        Parse `/etc/passwd` of the used image

        Returns:
            Dict of users
        """
        content = self.guest().cat('/etc/passwd').split("\n")
        return util.parse_passwd(content)

    def guest_user_home(self, name):
        """get user home from image

        Get home directory of a user of the used image

        Returns:
            Home path or None if user was not found
        """
        users = self.guest_get_users()
        if name not in users:
            return None

        return users[name]["home"]

    def guest_get_groups(self):
        """get groups from image

        Parse `/etc/group` of the used image

        Returns:
            List of groups
        """
        content = self.guest().cat('/etc/group').split("\n")
        return util.parse_groups(content)
