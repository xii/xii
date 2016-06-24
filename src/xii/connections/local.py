import os
import getpass
import urllib2
import errno
import stat

from xii import connection, error
from xii.output import progress


BUF_SIZE = 16 * 1024


class Local(connection.Connection):
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

    def exists(self, path):
        try:
            os.stat(path)
        except OSError as err:
            if err.errno == errno.ENOENT:
                return False
            raise
        return True

    def user(self):
        return getpass.getuser()

    def user_home(self):
        return os.path.expanduser('~')

    def copy(self, msg, source_path, dest_path):
        size = os.path.getsize(source_path)
        try:
            with open(source_path, 'rb') as source:
                with open(dest_path, 'wb') as dest:
                    self._copy_stream(msg, size, source, dest)
        except OSError as err:
            raise error.FileError(source_path, "Could not copy file: {}".format(err))

    def chmod(self, path, new_mode, append=False):
        mode = new_mode
        if append:
            mode = os.stat(path).st_mode | new_mode
        os.chmod(path, mode)

    def download(self, msg, url, dest_path):
        source = urllib2.urlopen(url)
        size = int(source.info().getheaders("Content-Length")[0])

        with open(dest_path, 'wb') as dest:
            self._copy_stream(msg, size, source, dest)

    def _copy_stream(self, msg, size, source, dest):
        copied = 0
        while True:
            buf = source.read(BUF_SIZE)
            if not buf:
                break
            dest.write(buf)
            copied += len(buf)
            progress(msg, size, copied)
