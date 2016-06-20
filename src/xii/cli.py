
import argparse

from output import set_verbose, fatal
from command import CommandRegister

import commands
import components
import properties


def usage_text():
    usage = ["xii [OPTIONS] COMMAND [ARGS] ", "", "Commands available:"]
    for command_help in CommandRegister.available():
        usage.append("  " + command_help)
    return "\n".join(usage)


def run_cli():

    parser = argparse.ArgumentParser(usage=usage_text())
    parser.add_argument('--verbose', help="Verbose output", action='store_true', default=False)
    parser.add_argument('name', metavar="COMMAND", help="Command to execute")
    parser.add_argument('args', nargs=argparse.REMAINDER, metavar="ARGS", help="Command arguments")

    cmd      = parser.parse_args()
    instance = CommandRegister.get(cmd)

    if not instance:
        fatal("Invalid command `{}`. Command not found.".format(cmd.name))
        parser.print_help()
        return 1

    if cmd.verbose:
        set_verbose()

    try:
        return instance.run()
    except RuntimeError as e:
        fatal(str(e))
        return 1
