import argparse

from xii import definition, command, components


class ResumeCommand(command.Command):
    name = ["resume"]
    help = "resume all paused domains"

    def run(self):

        dfn_path = self.parse_command()

        dfn = definition.from_file(dfn_path, self.config)

        runtime = {
            "definition": dfn,
            "config": self.config,
            "userinterface": self.userinterface
        }

        cmpnts = components.from_definition(runtime)

        for cmpnt in cmpnts:
            cmpnt.run("resume")

    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("dfn_file", nargs="?", default=None)

        args = parser.parse_args(self.args)

        return args.dfn_file


command.Register.register(ResumeCommand)
