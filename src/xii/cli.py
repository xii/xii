
import argparse

from xii import commands, components, attributes, paths, config, command, error
from xii import store
from xii.error import XiiError
from xii.ui import warn


def usage_text():
    usage = ["xii [OPTIONS] COMMAND [ARGS] ", "", "Commands available:"]
    for command_help in command.Register.available():
        usage.append(command_help)
    return "\n".join(usage)


def cli_arg_parser():
    parser = argparse.ArgumentParser(usage=usage_text())
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Make output more verbose")
    parser.add_argument("--no-parallel", dest="parallel", action="store_false", default=True,
                        help="Disable parallel processing")
    parser.add_argument("--config", default=None,
                        help="Optional path to configuration file")

    parser.add_argument("-D", "--define", dest="defines", action="append",
                        help="Define local variables")
    parser.add_argument("-V", "--varfile", dest="varfile", default=None,
                       help="load local variables from file")
    parser.add_argument("command", metavar="COMMAND",
                        help="Command to run")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, metavar="ARGS",
                        help="Command arguments")

    return parser


def run_cli():
    parser = cli_arg_parser()
    try:

        # prepare local environment xii runs in
        paths.prepare_local_paths()
        # parse arguments
        cli_args = parser.parse_args()
        # load variable store
        store = Store()
        # load defaults / home configuration into variable store
        config = config.load_from_file(cli_args.config)
        # parse definifition file
        # merge with arguments from commandline
        # run command
        # return exit code

        cli_args = parser.parse_args()
        conf = config.Config(cli_args.config, cli_args)
        instance = command.Register.get(cli_args.command, cli_args.command_args, conf)

        if not instance:
            warn("Invalid command `{}`. Command not found.".format(cli_args.command))
            parser.print_help()
            return 1

        # if cli_args.verbose:
        #     set_verbose()

        return instance.run()
    except XiiError as e:
        it = iter(e.error())
        warn(e.error_title() + ": " + next(it))

        for line in it:
            warn(line)
        return 1
