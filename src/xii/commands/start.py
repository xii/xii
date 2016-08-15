import argparse

from xii import definition, command, components


def start_command(cmpnt):
    cmpnt.run("start")


class StartCommand(command.Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def run(self):

        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        dfn  = definition.from_file(args.dfn_file, self.config)

        runtime = self.make_runtime({
            "definition": dfn
        })

        cmpnts = components.from_definition(runtime)

        self.action_each("start", cmpnts)


command.Register.register(StartCommand)
