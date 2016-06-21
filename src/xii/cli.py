
import argparse

from xii import commands, components, attributes, paths, config, command
from xii.output import fatal, set_verbose, hr


def usage_text():
    usage = ["xii [OPTIONS] COMMAND [ARGS] ", "", "Commands available:"]
    for command_help in command.Register.available():
        usage.append("  " + command_help)
    return "\n".join(usage)


def run_cli():

    parser = argparse.ArgumentParser(usage=usage_text())
    parser.add_argument('--verbose', action='store_true', default=False, help="Verbose output")
    parser.add_argument('--config', default=None, help="Path to configuration file")
    parser.add_argument('command', metavar="COMMAND", help="Command to execute")
    parser.add_argument('command_args', nargs=argparse.REMAINDER, metavar="ARGS", help="Command arguments")

    try:

        paths.prepare_local_paths()

        cli_args = parser.parse_args()
        conf = config.Config(cli_args.config)

        instance = command.Register.get(cli_args.command, cli_args.command_args, conf)

        if not instance:
            fatal("Invalid command `{}`. Command not found.".format(cli_args.command))
            parser.print_help()
            return 1

        if cli_args.verbose:
            set_verbose()

        return instance.run()
    except RuntimeError as e:
        print("")
        fatal(hr("FATAL: "))
        fatal(str(e))
        fatal(hr(""))
        return 1
