import os
import argparse

from xii import definition, command


class StopCommand(command.Command):
    """Stop all running components of your environment

    This will stop all components including network setups.
    """
    name = "stop"
    help = "Stop xii instances"

    def run(self):
        self.each_component("stop")
