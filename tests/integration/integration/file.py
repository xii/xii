import os

def get_test_path(name):
    path = os.path.dirname(os.path.dirname(__file__))
    import pdb; pdb.set_trace()
    return os.path.join(path, "tests", name + ".xii")
