import argparse

from xii import command


def start_command(cmpnt):
    cmpnt.run("start")


class StartCommand(command.Command):
    name = ['start', 's']
    help = "load xii definition and start vm's"

    def run(self):
        self.each_component("start")
        self.finalize()
