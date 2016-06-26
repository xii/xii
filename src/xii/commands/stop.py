import os
import argparse

from xii import definition, command, components, connection
from xii.output import header, debug, hr, sep


class StopCommand(command.Command):
    name = ['stop']
    help = "Stop xii instances"

    def run(self):
        (dfn_path) = self.parse_command()

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

        args = parser.parse_args(self.args)

        return (args.dfn_file)


command.Register.register(StopCommand)
