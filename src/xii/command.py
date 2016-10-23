import argparse
import os

from multiprocessing import Pool
from xii.ui import HasOutput


def run_action_on_obj((obj, action)):
    obj.run(action)

class Command(HasOutput):
    name = ["invalidcommand"]
    help = "No help given"

    def __init__(self, args, store):
        self.args = args
        self.store = store

    def get_full_name(self):
        return ["cmd", self.name[0]]

    def run(self):
        pass
        

    def action_each(self, action, objs):
        if self.store.get("global/parallel", True):
            pool = Pool(self.store.get("global/workers", 3))
            table = []

            import pdb; pdb.set_trace()

            for obj in objs:
                table.append((obj, action))

            result = pool.map_async(run_action_on_obj, table).get()
        else:
            for obj in objs:
                obj.run(action)

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
