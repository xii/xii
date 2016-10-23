import os
import errno
import shutil
import string

from pkg_resources import resource_filename
from xii import util, error

def defaults(file):
    return resource_filename(__name__, os.path.join('defaults', file))


def template(file):
    path = resource_filename(__name__, os.path.join('templates', file))

    if not os.path.isfile(path):
        raise error.Bug("Could not find template {}".format(path))
    content = util.file_read(path)
    return string.Template(content)


def find_definition_file(path):
    if not path:
        cwd = os.getcwd()
        path = os.path.join(cwd, os.path.basename(cwd) + ".xii")

    if not os.path.exists(path):
        raise error.FileError("Could not open definition: No such file or directory")
    return path


def local(extend=""):
    return os.path.join(os.path.expanduser('~'), '.xii', extend)


def xii_home(home, extend=""):
    return os.path.join(home, ".xii", extend)


def prepare_local_paths():
    # make config dir
    try:
        os.makedirs(local())
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(local()):
            pass
        else:
            raise RuntimeError("Could not create local configuration")

    # copy default configuration
    if not os.path.isfile(local('config.yml')):
        try:
            shutil.copyfile(defaults('config.yml'), local('config.yml'))
        except shutil.Error as err:
            raise RuntimeError("Can not copy default configuration: {}".format(err))
