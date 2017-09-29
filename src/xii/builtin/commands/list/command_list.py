import datetime
from math import floor

from xii import definition, command, error
from xii.need import NeedLibvirt, NeedSSH


class ListCommand(command.Command):
    """List all currently defined components

    Currently not every component supports uptime, therefor no
    uptime is displayed nevertheless if it's running or not.

    ::

        $ xii ls
        TYPE           NAME                  HOST                  UPTIME        STATUS
        network        simple-cluster        qemu:///system        ---           NOT CREATED
        node           admin                 qemu:///system        ---           NOT CREATED
        node           worker-1              qemu:///system        ---           NOT CREATED
        node           worker-2              qemu:///system        ---           NOT CREATED

    """
    name = "list"
    help = "list all currently defined components"

    @classmethod
    def argument_parser(cls, parser):
        parser.add_argument("-d", "--definition", default=None,
                            help="Define which xii definition file should be used")

        parser.add_argument("--all", default=False, action="store_true",
                            help="Show all components defined by the xii")

        parser.add_argument("--host", default=None,
                            help="Specify host to connect to. (A libvirt url is required)")

        parser.add_argument("--only", type=str, default=None,
                            help="Show only secified components [nodes,pools,networks]")

    def _get_uptime(self, time):
        now  = datetime.datetime.now()
        delta = now - datetime.datetime.fromtimestamp(time)

        if delta.days > 1:
            return "{} days".format(delta.days)

        if delta.seconds / 3600 > 1:
            return "{} hours".format(floor(delta.seconds / 3600))

        if delta.seconds / 60 > 1:
            return "{} minutes".format(floor(delta.seconds / 60))
        return "{} seconds".format(delta.seconds)

    def run(self):
        rows = []
        for c in self.children():
            meta = c.fetch_metadata()

            create = "---"
            if meta is not None:
                created_at = float(meta["created"])
                create = self._get_uptime(created_at)

            rows.append((c.ctype,
                c.entity(),
                c.get_virt_url(),
                create,
                c.status()
                ))
        self.show_table(["type", "name", "host", "uptime", "status"], rows)
