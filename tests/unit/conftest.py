import os
import pytest


class __TestData():

    def __init__(self, request):
        self.request = request

    def _get_data_path(self, name):
        module  = self.request.module.__file__
        path, _ = os.path.split(module)
        return os.path.join(path, "data", name)

    def load(self, name):
        path = self._get_data_path(name)
        try:
            with open(path, 'r') as stream:
                content = stream.read()
            return unicode(content)
        except IOError as err:
            pytest.fail("[data] Could not load {}: {}"
                         .format(path, err))


@pytest.fixture
def data(request):
    return  __TestData(request)
