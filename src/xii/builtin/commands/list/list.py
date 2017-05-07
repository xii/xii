from xii import definition, command, error
from xii.need import NeedLibvirt, NeedSSH


class ListCommand(command.Command):
    """List all currently defined components
    """
    name = ['list', 'ls']
    help = "list all currently defined components"

    @classmethod
    def argument_parser(cls):
        parser = command.Command.argument_parser(cls.name[0])

        parser.add_argument("-d", "--definition", default=None,
                            help="Define which xii definition file should be used")

        parser.add_argument("--all", default=False, action="store_true",
                            help="Show all components defined by the xii")

        parser.add_argument("--host", default=None,
                            help="Specify host to connect to. (A libvirt url is required)")

        parser.add_argument("--only", type=str, default=None,
                            help="Show only secified components [nodes,pools,networks]")
        return parser

    def run(self):
        pass
