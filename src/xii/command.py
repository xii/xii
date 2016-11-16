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

    def __init__(self, args, store):
        Entity.__init__(self, self.name[0], store, parent=None)
        self._args = args
        self._create_components()

    # store() is already defined by Entity

    @abstractmethod
    def run(self):
        pass

    def add_component(self, component):
        self.add_child(component)

    def get_component(self, name):
        return self.get_child(name)

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
        else:

            try:
                self.each_child(action, reverse=False)
            except KeyboardInterrupt:
                raise error.Interrupted()


    def _create_components(self):
        for cmpnt in component.from_definition(self.store(), self):
            self.add_component(cmpnt)
        self.validate()

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)

        return parser

    def args(self):
        return self._args


class Register(object):
    registered = []

    @classmethod
    def get(cls, name, args, store):
        for command in cls.registered:
            if name in command.name:
                return command(args, store)
        return None

    @classmethod
    def available(cls):
        output = ["", "shortcut  action    description",
                  "-------------------------------"]
        for command in cls.registered:
            output.append(" {:9}{:10}{}".format(", ".join(command.name[1:]), command.name[0], command.help))
        output.append(" ")
        return output

    @classmethod
    def register(cls, command):
        cls.registered.append(command)
