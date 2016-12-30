import argparse

from multiprocessing import Pool

from xii import command


def destroy_component(cmpnt):
    cmpnt.run("destroy")

class DestroyCommand(command.Command):
    name = ['destroy', 'd']
    help = "Destroy xii vm's"

    def run(self):
        self.each_component("destroy", reverse=True)


    def parse_command(self):
        parser = argparse.ArgumentParser()
        # parser.add_argument("--force", action='store_true', default=False,
        #                     help="Force creation of new instances. Ignore statefile (will be overwritten)")
        parser.add_argument("dfn_file", nargs="?", default=None)

        args = parser.parse_args(self.args)

        return args.dfn_file
