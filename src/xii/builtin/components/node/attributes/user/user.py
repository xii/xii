import crypt
import random
import string
import os

from xii import need
from xii.validator import Dict, String, VariableKeys, Key, RequiredKey, Bool

from xii.components.node import NodeAttribute


class UserAttribute(NodeAttribute, need.NeedGuestFS):
    atype = "user"

    requires = ["image"]

    default_settings = {
        "username": "xii",
        "description": "xii generated user",
        "shell": "/bin/bash",
        "password": "xii",
        "skel": True,
        "n": 0
    }

    keys = Dict([VariableKeys(
        Dict([
            RequiredKey('password', String("password")),
            Key('description', String("A nice user")),
            Key('shell', String("/bin/bash")),
            Key('default', Bool(True))
            ])
        , example="username")])

    def default_user(self):
        if not self.settings():
            return "xii"

        for name, user in self.settings().items():
            if "default" in user:
                return name

        name = self.settings().iterkeys().next()

        self.say("Assuming default user for {} is {}..."
                 .format(self.component_entity(), name))
        return name

    def spawn(self):
        if not self.settings():
            return

        self.say("adding user/s...")

        guest = self.guest()
        shadow = guest.cat("/etc/shadow").split("\n")
        passwd = guest.cat("/etc/passwd").split("\n")
        groups = guest.cat("/etc/group").split("\n")

        user_index = 0
        for name, settings in self.settings().items():
            self.say("adding {}".format(name))
            user = self.default_settings.copy()
            user['username'] = name
            user['n'] = user_index
            user.update(settings)

            gid, groups = self._add_user_to_groups(groups, user)
            user['gid'] = gid

            uid, passwd = self._add_user_to_passwd(passwd, user)
            user['uid'] = uid

            shadow = self._add_user_to_shadow(shadow, user)

            self._mk_home(guest, user)

            user_index += 1

        guest.write("/etc/shadow", "\n".join(shadow))
        guest.write("/etc/passwd", "\n".join(passwd))
        guest.write("/etc/group", "\n".join(groups))

    def _add_user_to_shadow(self, shadow, user):
        new = self._gen_shadow(user['username'], user['password'])
        for i, line in enumerate(shadow):
            if line.startswith(user['username'] + ":"):
                shadow[i] = new
                return shadow
        shadow.append(new)
        return shadow

    def _add_user_to_passwd(self, passwd, user):
        # Assumption: Every system already has a root user
        if user['username'] == "root":
            return 0, passwd

        uid = 1100 + user['n']

        if 'uid' in user:
            uid = user['uid']

        new = self._gen_passwd(uid, user)
        for i, line in enumerate(passwd):
            if line.startswith(user['username'] + ":"):
                passwd[i] = new
                return uid, passwd
        passwd.append(new)
        return uid, passwd

    def _add_user_to_groups(self, groups, user):

        # Since root group is defined in lsb it must be there
        if user['username'] == 'root':
            return 0, groups

        search = user['username']
        name = user['username']
        gid = 1100 + user['n']

        # if group is set use this
        if 'group' in user:
            search = user['group']
            name = user['group']

        # prefer gid over group name
        if 'gid' in user:
            search = str(user['gid'])
            gid = user['gid']

        for i, line in enumerate(groups):
            if ":" + search + ":" in line:
                if line[-1] != ":":
                    groups[i] += ","
                groups[i] += user['username']
                return gid, groups

        new = ":".join([name, "x", str(gid), user['username']])
        groups.append(new)

        return gid, groups

    def _gen_passwd(self, uid, user):
        home = self._user_home(user)
        elems = [user['username'],
                 "x",  # password is stored in /etc/shadow
                 str(uid),
                 str(user['gid']),
                 user['description'],
                 home,
                 user['shell']]
        return ":".join(elems)

    def _mk_home(self, guest, user):
        home = self._user_home(user)

        if guest.is_dir(home):
            return

        if user['skel']:
            guest.cp_r('/etc/skel', home)
        else:
            guest.mkdir(home)

        paths = [os.path.join(home, path) for path in guest.ls(home)]
        paths.append(home)

        for path in paths:
            guest.chown(user['uid'], user['gid'], path)

    def _user_home(self, user):
        if 'home' in user:
            return user['home']
        return os.path.join('/home', user['username'])

    def _gen_shadow(self, user, password):
        salt = self._generate_salt()
        hashed = crypt.crypt(password, "$6$" + salt + "$")
        return ":".join([user, hashed, "1", "", "99999", "", "", "", ""])

    def _generate_salt(self, length=16):
        chars = string.ascii_letters + string.digits
        return ''.join([random.choice(chars) for _ in range(length)])
