import os
import getpass
import urllib2
import errno
import shutil

from xii import error, util
from xii.connection import Connection


BUF_SIZE = 16 * 1024


class Local(Connection):

    def open(self, path, mode):
        return open(path, mode)

    def mkdir(self, directory, recursive=False):
        try:
            if recursive:
                os.makedirs(directory)
            else:
                os.mkdir(directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory):
                pass
            else:
                raise

    def stat(self, path):
        return os.stat(path)

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

    def copy(self, source_path, dest_path):
        size = os.path.getsize(source_path)
        try:
            with open(source_path, 'rb') as source:
                with open(dest_path, 'wb') as dest:
                    self._copy_stream(size, source, dest)
        except OSError as err:
            raise error.ExecError(source_path, "Could not copy file: {}".format(err))

    def chmod(self, path, new_mode, append=False):
        if append:
            new_mode = os.stat(path).st_mode | new_mode
        os.chmod(path, new_mode)

    def chown(self, path, uid, gid):
        os.chown(path, uid, gid)

    def download(self, url, dest_path):
        source = urllib2.urlopen(url)
        size = int(source.info().getheaders("Content-Length")[0])
        with open(dest_path, 'wb') as dest:
            self._copy_stream(size, source, dest)

    def get_users(self):
        try:
            with self.open('/etc/passwd', 'r') as source:
                return util.parse_passwd([line.rstrip('\n') for line in source])
        except OSError as err:
            raise error.ExecError("Reading /etc/passwd failed.")

    def get_groups(self):
        try:
            with self.open('/etc/group', 'r') as source:
                return util.parse_groups([line.rstrip('\n') for line in source])
        except OSError as err:
            raise error.ExecError("Reading /etc/group failed.")

    def _copy_stream(self, size, source, dest):
        copied = 0
        while True:
            buf = source.read(BUF_SIZE)
            if not buf:
                break
            dest.write(buf)
            copied += len(buf)
