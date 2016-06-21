import os
import errno
import shutil
import string

from pkg_resources import resource_filename
from xii import util

def defaults(file):
    return resource_filename(__name__, os.path.join('defaults', file))

def template(file):
    path = resource_filename(__name__, os.path.join('templates', file))

    if not os.path.isfile(path):
        raise Bug("Could not find template {}".format(path))
    content = util.file_read(path)
    return string.Template(content)


def local(file):
    return os.path.join(local_config_dir(), file)


def local_config_dir():
    return os.getenv("XDG_CONFIG_HOME", os.path.join(os.path.expanduser('~'), '.config/xii'))

def xii_storage(connection):
    pass

def xii_images(connection):
    pass

def prepare_local_paths():

    # make config dir
    try:
        os.makedirs(local_config_dir())
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(local_config_dir()):
            pass
        else:
            raise RuntimeError("Could not create local configuration")

    # copy default configuration
    if not os.path.isfile(local('config.yml')):
        try:
            shutil.copyfile(defaults('config.yml'), local('config.yml'))
        except shutil.Error as err:
            raise RuntimeError("Can not copy default configuration: {}".format(err))





