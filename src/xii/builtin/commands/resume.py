from xii import definition, command


class ResumeCommand(command.Command):
    name = ["resume"]
    help = "resume all paused domains"

    def run(self):
        parser = self.default_arg_parser()
        args = parser.parse_args(self.args())
        
        self.each_component("resume")


command.Register.register(ResumeCommand)
