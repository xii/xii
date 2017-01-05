from xii import definition, command


class ResumeCommand(command.Command):
    name = ["resume"]
    help = "resume all paused domains"

    def run(self):
        self.each_component("resume")
