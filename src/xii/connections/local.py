import os
import getpass
import errno
import shutil
import subprocess

from urllib.request import urlopen
from threading import Lock

from xii import error, util
from xii.connection import Connection


SUDO_LOCK = Lock()
BUF_SIZE = 16 * 1024


class Local(Connection):

    def open(self, path, mode):
        return open(path, mode)

    def mkdir(self, directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory):
                pass
            else:
                raise

    def stat(self, path):
        return os.stat(path)

    def which(self, executable):
        def can_exec(file_path):
            return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

        path, name = os.path.split(executable)
        if path:
            if can_exec(executable):
                return executable
        else:
            for p in os.environ["PATH"].split(os.pathsep):
                test = os.path.join(p.strip('"'), executable)
                if can_exec(test):
                    return test
        return None

    def exists(self, path):
        try:
            os.stat(path)
        except OSError as err:
            if err.errno == errno.ENOENT:
                return False
            raise
        return True

    def rm(self, path):
        shutil.rmtree(path)

    def user(self):
        return getpass.getuser()

    def user_home(self):
        return os.path.expanduser('~')

    def copy(self, source, dest):
        size = os.path.getsize(source)
        try:
            with open(source, 'rb') as s:
                with open(dest, 'wb') as d:
                    self._copy_stream(size, s, d)
        except OSError:
            return False
        return True

    def upload(self, source, dest):
        return self.copy(source, dest)

    def download(self, source, dest):
        return self.copy(source, dest)

    def download_url(self, url, dest):
        source = urlopen(url)
        size = int(source.info().getheaders("Content-Length")[0])
        with open(dest, 'wb') as d:
            self._copy_stream(size, source, d)

    def chmod(self, path, new_mode, append=False):
        if append:
            new_mode = os.stat(path).st_mode | new_mode
        os.chmod(path, new_mode)

    def chown(self, path, uid, gid):
        os.chown(path, uid, gid)

    def get_users(self):
        try:
            with self.open('/etc/passwd', 'r') as source:
                return util.parse_passwd([line.rstrip('\n') for line in source])
        except OSError:
            raise error.ExecError("Reading /etc/passwd failed.")

    def get_groups(self):
        try:
            with self.open('/etc/group', 'r') as source:
                return util.parse_groups([line.rstrip('\n') for line in source])
        except OSError:
            raise error.ExecError("Reading /etc/group failed.")

    def call(self, command, *args):
        process = subprocess.Popen([command] + list(args),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        return (process.stdout.read(), process.returncode)

    def sudo_call(self, command, *args):
        SUDO_LOCK.acquire()
        print("Want to run '{}' as root:".format(command))
        process = subprocess.Popen(["sudo", command] + list(args),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        SUDO_LOCK.release()
        return (process.stdout.read(), process.returncode)

    def _copy_stream(self, size, source, dest):
        copied = 0
        while True:
            buf = source.read(BUF_SIZE)
            if not buf:
                break
            dest.write(buf)
            copied += len(buf)
