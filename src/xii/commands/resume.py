from xii import definition, command, components


class ResumeCommand(command.Command):
    name = ["resume"]
    help = "resume all paused domains"

    def run(self):

        parser = self.default_arg_parser()
        args = parser.parse_args(self.args)

        dfn = definition.from_file(args.dfn_file, self.config)

        runtime = self.make_runtime({
            "definition": dfn
        })

        cmpnts = components.from_definition(runtime)

        self.action_each("resume", cmpnts)


command.Register.register(ResumeCommand)
