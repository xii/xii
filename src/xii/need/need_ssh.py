import md5

from xii import error
from xii.output import HasOutput
from xii.connections.ssh import Ssh


class NeedSSH(HasOutput):
    def get_default_user(self):
        return None

    def get_default_host(self):
        return None

    def get_default_password(self):
        return None

    def default_ssh(self):
        user = self.get_default_user()
        host = self.get_default_host()

        if not user or not host:
            raise error.ConnError("Could not connect to ssh. "
                                  "Invalid configuration")

        return self.ssh(user, host)

    def ssh(self, host, user):
        connection_hash = self._generate_hash(host, user)
        retry = self.get_config().retry("ssh", default=20)
        wait = self.get_config().wait(default=5)

        def _create_ssh_conn():
            ssh = Ssh(self, host, user, retry, wait)
            return ssh

        def _close_ssh_conn(ssh):
            ssh.close()

        return self.share(connection_hash, _create_ssh_conn, _close_ssh_conn)

    def _generate_hash(self, host, user):
        return "ssh" + md5.new("{}-{}".format(host, user)).hexdigest()
