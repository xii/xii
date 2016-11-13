import os
import argparse

from xii import definition, command 


class StopCommand(command.Command):
    name = ['stop']
    help = "Stop xii instances"

    def run(self):

        parser = self.default_arg_parser()
        args = parser.parse_args(self.args())

        self.each_component("stop")


command.Register.register(StopCommand)
