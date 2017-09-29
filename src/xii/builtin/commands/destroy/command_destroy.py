import argparse

from multiprocessing import Pool

from xii import command


def destroy_component(cmpnt):
    cmpnt.run("destroy")

class DestroyCommand(command.Command):
    name = "destroy"
    help = "Destroy xii vm's"

    def run(self):
        self.each_component("destroy", reverse=True)
