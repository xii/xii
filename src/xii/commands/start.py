import os
import argparse

from xii import definition, command, components, connection
from xii.output import header, debug, hr, sep


class StartCommand(command.Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def run(self):

        (dfn_path, forced_stop) = self.parse_command()

        dfn  = definition.from_file(dfn_path, self.conf)
        conn = connection.establish(dfn, self.conf)

        cmpnts = components.from_definition(dfn, self.conf, conn)

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

        return (args.dfn_file, args.force)


command.Register.register(StartCommand)
