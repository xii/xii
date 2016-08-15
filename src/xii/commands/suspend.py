from xii import definition, command, components


class SuspendCommand(command.Command):
    name = ["suspend"]
    help = "Suspend all running instances"

    def run(self):
        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        dfn = definition.from_file(args.dfn_file, self.config)

        runtime = self.make_runtime({
            "definition": dfn
        })

        cmpnts = components.from_definition(runtime)

        self.action_each("suspend", cmpnts)

command.Register.register(SuspendCommand)
