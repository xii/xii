import os
import argparse

from xii import definition, command, components, connection


class StopCommand(command.Command):
    name = ['stop']
    help = "Stop xii instances"

    def run(self):

        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        dfn  = definition.from_file(args.dfn_file, self.config)

        runtime = self.make_runtime({
            "definition": dfn
        })

        cmpnts = components.from_definition(runtime)

        self.action_each("stop", cmpnts)


command.Register.register(StopCommand)
