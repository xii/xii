import os
import argparse

from xii.definition import load_from_file
from xii.command import Command, CommandRegister
from xii.output import info, warn


class StartCommand(Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--force", action='store_true', default=False,
                            help="Force creation of new instances. Ignore statefile (will be overwritten)")
        parser.add_argument("file", nargs="?", default=None)

        settings          = parser.parse_args(self.args)
        self.def_file     = os.path.abspath(settings.file)
        self.forced_start = settings.force

    def find_def_file(self):
        if not self.def_file:
            def_file = os.path.dirname(os.getcwd()) + ".xii"
            if os.path.exists(def_file):
                self.def_file = def_file
            else:
                raise RuntimeError("Could not find a sustainable xii definition")
        else:
            if not os.path.isfile(self.def_file):
                raise RuntimeError("Could not open xii definition. "
                                   "No such file or directory")

    def run(self):
        self.parse_command()
        self.find_def_file()
        self.already_running()

        definition = load_from_file(self.def_file)

        info("Starting instances")
        map(lambda c: c.is_ready(), definition.components())
        map(lambda c: c.start(), definition.componentes())



    def already_running(self):
        pass

CommandRegister.register(StartCommand)
