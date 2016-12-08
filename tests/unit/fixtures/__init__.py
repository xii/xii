import os
import codecs
import yaml
import pytest

def __get_path(file):
    path, _ = os.path.split(__file__)
    return os.path.join(path, file)

def load_fixture(file):
    path = __get_path(file + ".yml")
    try:
        with open(path, 'r') as stream:
            return yaml.load(stream)
    except IOError as err:
        pytest.fail("Could not find fixture: {}".format(err), pytrace=False)

def load_raw_fixture(file):
    path = __get_path(file)
    try:
        with codecs.open(path, "r", "utf-8") as stream:
            return stream.read()
    except IOError as err:
        pytest.fail("Could not find fixture: {}".format(err), pytrace=False)
        


