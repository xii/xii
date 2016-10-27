from xii import definition, command


class SuspendCommand(command.Command):
    name = ["suspend"]
    help = "Suspend all running instances"

    def run(self):
        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        self.each_component("suspend")


command.Register.register(SuspendCommand)
