import argparse

from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from abc import ABCMeta, abstractmethod

from xii import error
from xii.store import HasStore
from xii.entity import Entity


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

    def each_component(self, action, reverse=False):
        try:
            if self.get("global/parallel", True):
                try:
                    self._run_parallel(self.get("global/workers", 3), action, reverse)
                except Exception as err:
                    self.warn("thread failed. stopping immediately!")
                    raise err
            else:
                self.each_child(action, reverse)
        except KeyboardInterrupt:
            raise error.Interrupted()


    # overwrite behaviour from entity class. Search for ctype instead
    # of the entity name
    def _child_index(self, ctype):
        for idx, child in enumerate(self._childs):
            if child.ctype == ctype:
                return idx
        return None

    def _run_parallel(self, workers, action, reverse, args=[]):
        def run_action(obj):
            obj.run(action)

        try:
            executor = ThreadPoolExecutor(workers)
            futures = map(partial(executor.submit, run_action), reversed(self.children()))

            # handle possible errors
            errors = filter(None, map(Future.exception, futures))

            if errors:
                for err in errors:
                    raise err
        finally:
            executor.shutdown(wait=False)

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)
        return parser

    def args(self):
        return self._args
