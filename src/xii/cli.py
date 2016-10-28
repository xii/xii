
import argparse

from xii import paths, config, command, util, definition, extension
from xii.store import Store
from xii.error import XiiError
from xii.output import warn


def usage_text():
    usage = ["xii [OPTIONS] COMMAND [ARGS] ", "", "Commands available:"]
    for command_help in command.Register.available():
        usage.append(command_help)
    return "\n".join(usage)


def cli_arg_parser():
    parser = argparse.ArgumentParser(usage=usage_text())
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Make output more verbose and dump environment")
    parser.add_argument("--no-parallel", dest="parallel", action="store_false", default=True,
                        help="Disable parallel processing")
    parser.add_argument("--config", default=None,
                        help="Optional path to configuration file")

    parser.add_argument("-D", "--define", dest="defines", action="append", default=[],
                        help="Define local variables")
    #parser.add_argument("-V", "--varfile", dest="varfile", default=None,
    #                   help="load local variables from file")
    parser.add_argument("command", metavar="COMMAND",
                        help="Command to run")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, metavar="ARGS",
                        help="Command arguments")

    return parser


def run_cli():
    extension.load_builtin()
    parser = cli_arg_parser()
    try:

        # prepare local environment xii runs in
        paths.prepare_local_paths()

        # parse arguments
        cli_args = parser.parse_args()

        # load variable store
        store = Store()
        store.set("runtime/config", paths.local("config.yml"))

        store.set("runtime/definition", paths.find_definition_file(cli_args.config))

        # load defaults / home configuration into variable store
        config = util.yaml_read(store.get("runtime/config"))

        store.set("global", config)

        if cli_args.parallel is False:
            store.set("global/parallel", cli_args.parallel)

        # merge with arguments from commandline
        for define in [d.split("=") for d in cli_args.defines]:
            if len(define) != 2:
                warn("Invalid variable definition detected")
                warn("Use -Dscope/variable=value")
                return 1
            store.set(define[0], util.convert_type(define[1]))

        # parse definifition file
        defn = util.jinja_read(store.get("runtime/definition"), store)

        # construct component configurations
        definition.prepare_store(defn, store)
        
        # run command
        instance = command.Register.get(cli_args.command, cli_args.command_args, store)
        # return exit code

        if not instance:
            warn("Invalid command `{}`. Command not unknown.".format(cli_args.command))
            return 1
        
        return instance.run()
    except XiiError as e:
        it = iter(e.error())
        warn(e.error_title() + ": " + next(it))

        for line in it:
            warn(line)

        if cli_args.debug:
            store.dump()
        return 1
