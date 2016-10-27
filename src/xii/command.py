import argparse
import os

from abc import ABCMeta, abstractmethod
from multiprocessing import Pool


from xii import component
from xii.output import HasOutput
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

    def each_component(self, action):
        components = self.get("components")

        if self.get("global/parallel", True):
            pool = Pool(self.get("global/workers", 3))
            table = []

            for cmpnt in self.children():
                table.append((cpmnt, action))

            result = pool.map_async(run_action_on_obj, table).get()
        else:
            for obj in objs:
                self.each_child(action, reverse=False)

    def _create_components(self):
        for cmpnt in component.from_definition(self.store(), self):
            self.add_component(cmpnt)
        self.validate()

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)

        return parser


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
