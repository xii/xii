from xii import definition, command


class SuspendCommand(command.Command):
    name = ["suspend"]
    help = "Suspend all running instances"

    def run(self):
        self.each_component("suspend")
