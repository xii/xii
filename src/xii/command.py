import argparse

from multiprocessing import Pool, Queue
import logging, multiprocessing
mpl = multiprocessing.log_to_stderr()
mpl.setLevel(multiprocessing.SUBDEBUG)
from xii.ui import HasOutput


def run_action_on_obj((obj, action)):
    try:
        # This is where you do your actual work
        return obj.run(action)
    except:
        # Put all exception text into an exception and raise that
        raise Exception("".join(traceback.format_exception(*sys.exc_info())))

class Command(HasOutput):
    name = ["invalidcommand"]
    help = "No help given"

    def __init__(self, args, config):
        self.args = args
        self.config = config

    def get_full_name(self):
        return ["cmd", self.name[0]]

    def run(self):
        pass

    def action_each(self, action, objs):
        if self.config.is_parallel():

            pool = Pool(self.config.workers())
            table = []

            for obj in objs:
                table.append((obj, action))

            result = pool.map_async(run_action_on_obj, table).get()
        else:
            for obj in objs:
                obj.run(action)

    def make_runtime(self, additional={}):
        runtime = {
            "config": self.config,
        }
        runtime.update(additional)
        return runtime

    def default_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)

        return parser



class Register(object):
    registered = []

    @classmethod
    def get(cls, name, args, config):
        for command in cls.registered:
            if name in command.name:
                return command(args, config)
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
