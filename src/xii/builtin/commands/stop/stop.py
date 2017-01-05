import os
import argparse

from xii import definition, command


class StopCommand(command.Command):
    name = ['stop']
    help = "Stop xii instances"

    def run(self):
        self.each_component("stop")
