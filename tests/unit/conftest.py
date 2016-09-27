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


class MockedSleep():

    def __init__(self):
        self._call_count = 0
        self._sleep_time  = 1

    def set_sleep_time(self, n):
        self._sleep_time = n

    def call_count(self):
        return self._call_count

    def __call__(self, sleep):
        if sleep != self._sleep_time:
            pytest.fail("[sleep] Tought sleeping {} seconds "
                        "but {} where requrested"
                        .format(sleep, time))
        self._call_count += 1


@pytest.fixture
def sleep(monkeypatch, request):
    fake_sleep = MockedSleep()
    monkeypatch.setattr("time.sleep", lambda n: fake_sleep(n))

    return fake_sleep
