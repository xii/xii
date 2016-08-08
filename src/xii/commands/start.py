import os
import argparse

from multiprocessing import Pool

from xii import definition, command, components, connection
from xii.output import header, debug, hr, sep


class StartCommand(command.Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def run(self):

        (dfn_path, forced_destroy) = self.parse_command()

        dfn  = definition.from_file(dfn_path, self.config)

        runtime = {
                'definition': dfn,
                'config': self.config,
                'userinterface': self.userinterface
        }

        cmpnts = components.from_definition(runtime)

        for cmpnt in cmpnts:
            cmpnt.run("start")


    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--force", action='store_true', default=False,
                            help="Force creation of new instances. Ignore statefile (will be overwritten)")
        parser.add_argument("dfn_file", nargs="?", default=None)

        args = parser.parse_args(self.args)

        return (args.dfn_file, args.force)


command.Register.register(StartCommand)
