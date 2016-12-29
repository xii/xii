import argparse
import multiprocessing
import signal

from abc import ABCMeta, abstractmethod


from xii import component, error
from xii.store import HasStore
from xii.entity import Entity


def run_action_on_obj((obj, action)):
    obj.run(action)

class Command(Entity, HasStore):
    __meta__ = ABCMeta

    name = ["invalidcommand"]
    help = "No help given"

    def __init__(self, args, tpls, store):
        Entity.__init__(self, self.name[0], store, parent=None, templates=tpls)
        self._args = args

    # store() is already defined by Entity

    @abstractmethod
    def run(self):
        pass

    def add_component(self, component):
        self.add_child(component)

    def get_component(self, name):
        return self.get_child(name)

    def has_component(self, ctype, cmpnt):
        components = self.get("components")

        if not components:
            return False

        if (ctype not in components or
            cmpnt not in components[ctype][cmpnt]):
            return False
        return True

    def each_component(self, action):

        def _init_worker():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        components = self.get("components")

        if self.get("global/parallel", True):
            pool = multiprocessing.Pool(self.get("global/workers", 3), _init_worker)
            table = []

            for cmpnt in self.children():
                table.append((cmpnt, action))

            try:
                pool.map_async(run_action_on_obj, table).get()
                pool.close()
            except KeyboardInterrupt:
                pool.terminate()
                raise error.Interrupted()
            except Exception as err:
                self.warn("thread failed. stopping immediately!")
                pool.terminate()
                raise err
        else:

            try:
                self.each_child(action, reverse=False)
            except KeyboardInterrupt:
                raise error.Interrupted()

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)
        return parser

    def args(self):
        return self._args
