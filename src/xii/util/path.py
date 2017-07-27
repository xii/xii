import os
import time
import errno
import shutil
import string

from pkg_resources import resource_filename
from xii import error
from xii.util.misc import md5digest


def local(extend=""):
    return os.path.join(os.path.expanduser('~'), '.xii', extend)

def defaults(file):
    return resource_filename("xii", os.path.join('defaults', file))


def resource_from_path(path, ext=".py"):
    name = os.path.basename(path)
    return os.path.join(path, name + ext)


def make_temp_name(seed):
    hashed = md5digest(seed + str(time.time()))
    return "/tmp/xii-" + hashed

def find_definition_file(path):
    if path is None:
        pwd = os.getcwd()
        path = os.path.join(pwd, os.path.basename(pwd) + ".xii")
    else:
        path = os.path.abspath(path)
    if not os.path.exists(path):
        raise error.NotFound("{}: No such file or directory.".format(path))
    return path




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
