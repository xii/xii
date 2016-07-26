import os
import argparse

from xii import definition, command, components, connection
from xii.output import header, debug, hr, sep


class StopCommand(command.Command):
    name = ['stop']
    help = "Stop xii instances"

    def run(self):
        dfn_path, force = self.parse_command()

        dfn  = definition.from_file(dfn_path, self.conf)
        conn = connection.establish(dfn, self.conf)

        cmpnts = components.from_definition(dfn, self.conf, conn)

        for cmpnt in cmpnts:
            header("Stoping {}".format(cmpnt.name))
            cmpnt.info()
            hr(sep(""))
            cmpnt.action('stop')

    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)
        parser.add_argument("--force", action='store_true', default=False,
                            help="Force shutdown.")

        args = parser.parse_args(self.args)

        return args.dfn_file, args.force


command.Register.register(StopCommand)
