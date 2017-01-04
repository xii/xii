import os
import argparse

from xii import paths, command, util, definition, component
from xii.extension import ExtensionManager
from xii.store import Store
from xii.error import XiiError, Interrupted
from xii.output import warn


def usage_text(ext_mgr):
    usage = ["xii [OPTIONS] COMMAND [ARGS] ", "", "Commands available:"]
    for info in ext_mgr.commands_available():
        usage.append(info)
    return "\n".join(usage)


def cli_arg_parser(ext_mgr):
    parser = argparse.ArgumentParser(usage=usage_text(ext_mgr))
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Make output more verbose and dump environment")
    parser.add_argument("--deffile", default=None,
                        help="Specify definition file")
    parser.add_argument("--no-parallel", dest="parallel", action="store_false", default=True,
                        help="Disable parallel processing")
    parser.add_argument("-D", "--define", dest="defines", action="append", default=[],
                        help="Define local variables")
    #parser.add_argument("-V", "--varfile", dest="varfile", default=None,
    #                   help="load local variables from file")
    parser.add_argument("command", metavar="COMMAND",
                        help="Command to run")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, metavar="ARGS",
                        help="Command arguments")

    return parser


def init_runtime(store, args):
    store.set("runtime/config", paths.local("config.yml"))

    store.set("runtime/definition", paths.find_definition_file(args.deffile))

    # load defaults / home configuration into variable store
    config = util.yaml_read(store.get("runtime/config"))

    store.set("global", config)

    if args.parallel is False:
        store.set("global/parallel", args.parallel)

    # merge with arguments from commandline
    for define in [d.split("=") for d in args.defines]:
        if len(define) != 2:
            warn("Invalid variable definition detected")
            warn("Use -Dscope/variable=value")
            return 1
        store.set(define[0], util.convert_type(define[1]))

    for envvar in filter(lambda x: x.startswith("XII_"), os.environ):
        store.set(envvar[4:], os.environ[envvar])


def prepare_command(command, ext_mgr):
    definition = command.get("components")
    for cmpnt in component.from_definition(definition, command, ext_mgr):
        command.add_component(cmpnt)
    command.validate()


def run_cli():
    try:

        # load all components
        ext_mgr = ExtensionManager()
        ext_mgr.add_builtin_path()
        ext_mgr.load()

        # prepare local environment xii runs in
        paths.prepare_local_paths()

        # parse arguments
        parser = cli_arg_parser(ext_mgr)
        cli_args = parser.parse_args()

        # load variable store
        store = Store()

        # initialize variables
        init_runtime(store, cli_args)

        # parse definifition file
        defn = util.jinja_read(store.get("runtime/definition"), store)

        # construct component configurations
        definition.prepare_store(defn, store)

        # get command
        cmd = ext_mgr.get_command(cli_args.command)

        if not cmd:
            warn("Invalid command `{}`. Command not unknown."
                 .format(cli_args.command))
            return 1

        instance = cmd["class"](cli_args.command_args, cmd["templates"], store)
        prepare_command(instance, ext_mgr)

        return instance.run()
    except Interrupted:
        warn("interrupted... stopping immediately!")
        return 1

    except XiiError as e:
        it = iter(e.error())
        warn(e.error_title() + ": " + next(it))

        for line in it:
            warn(line)

        if cli_args.debug:
            store.dump()
        return 1
