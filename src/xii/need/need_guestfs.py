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

    def guest_get_users(self):
        users = {}
        content = self.guest().cat('/etc/passwd').split("\n")

        for line in content:
            user = line.split(":")
            if len(user) < 6:
                continue
            users[user[0]] = {
                    'uid': int(user[2]),
                    'gid': int(user[3]),
                    'description': user[4],
                    'home': user[5],
                    'shell': user[6]}
        return users

    def guest_user_home(self, name):
        users = self.guest_get_users()
        if name not in users:
            return None

        return users[name]["home"]

    def guest_get_groups(self):
        groups = {}
        content = self.guest().cat('/etc/group').split("\n")

        for line in content:
            group = line.split(":")
            if len(group) < 2:
                continue

            groups[group[0]] = {'gid': int(group[2]), 'users': []}

            if len(group) > 2:
                groups[group[0]]['users'] = group[3].split(',')
        return groups
