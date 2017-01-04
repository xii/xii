import argparse

from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from abc import ABCMeta, abstractmethod

from xii import error
from xii.store import HasStore
from xii.entity import Entity


# move me to util if time is ready
def in_parallel(worker_count, objects, executor):
    try:
        pool = ThreadPoolExecutor(worker_count)
        futures = map(partial(pool.submit, executor), objects)

        # handle possible errors
        errors = filter(None, map(Future.exception, futures))

        if errors:
            for err in errors:
                raise err
    finally:
        pool.shutdown(wait=False)


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
                count = self.get("global/workers", 3)
                for name, group in self._grouped_components():
                    self.say("{}ing {}s..".format(action, name))
                    in_parallel(count, group, lambda o: o.run(action))
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

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)
        return parser

    def args(self):
        return self._args

    def child_index(self, component):
        for idx, child in enumerate(self._childs):
            if child.ctype == component:
                return idx
        return None

    def _grouped_components(self):
        self.reorder_childs();
        groups = []
        childs = self.children()
        name = childs[0].ctype
        next = [childs[0]]

        for child in childs[1:]:
            if child.ctype == name:
                next.append(child)
            else:
                groups.append((name, next))
                name = child.ctype
                next = [child]
        groups.append((name, next))
        return groups
