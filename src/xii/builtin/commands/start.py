import argparse

from xii import command


def start_command(cmpnt):
    cmpnt.run("start")


class StartCommand(command.Command):
    name = ['start', 's']
    help = "Load xii definition and start vm's"

    def run(self):

        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        self.each_component("start")

command.Register.register(StartCommand)
