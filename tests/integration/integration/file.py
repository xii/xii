import os

def get_test_path(name):
    path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(path, "tests", name + ".xii")
