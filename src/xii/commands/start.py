import os
import argparse

from xii import definition, command, components, connection
from xii.output import header, debug, hr, sep


class StartCommand(command.Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def run(self):
        self.parse_command()

        self.find_dfn_file()

        if not self.already_running() or self.forced_start:
            if self.forced_start:
                # call destroy
                pass

            debug("Loading configuration")
            dfn  = definition.from_file(self.dfn_file, self.conf)
            conn = connection.establish(dfn, self.conf)

            cmpnts = components.from_definition(dfn, self.conf, conn)

            map(lambda cpmnt: cpmnt.is_ready(), cmpnts)

            for cmpnt in cmpnts:
                header("Starting {}".format(cmpnt.name))
                cmpnt.info()
                hr(sep(""))
                cmpnt.action('start')

    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--force", action='store_true', default=False,
                            help="Force creation of new instances. Ignore statefile (will be overwritten)")
        parser.add_argument("dfn_file", nargs="?", default=None)

        args = parser.parse_args(self.args)

        self.dfn_file     = args.dfn_file
        self.forced_start = args.force

    def find_dfn_file(self):
        if not self.dfn_file:
            dfn_file = os.path.dirname(os.getcwd()) + ".xii"
            if os.path.exists(dfn_file):
                self.dfn_file = dfn_file
            else:
                raise RuntimeError("Could not find a sustainable xii definition")
        else:
            self.dfn_file = os.path.abspath(self.dfn_file)
            if not os.path.isfile(self.dfn_file):
                raise RuntimeError("Could not open xii definition. "
                                   "No such file or directory")

    def already_running(self):
        pass

command.Register.register(StartCommand)
