import os
import argparse

from xii import paths, util, definition, component
from xii.extension import ExtensionManager
from xii.store import Store
from xii.error import XiiError, Interrupted, Bug, NotFound
from xii.output import warn


def prepare_command_instance(command, ext_mgr):
    definition = command.get("components")
    for cmpnt in component.from_definition(definition, command, ext_mgr):
        command.add_component(cmpnt)
    command.validate()


def cli_arg_parser(ext_mgr):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(metavar="COMMAND", dest="command")

    parser.add_argument("definition",
                        metavar="DEFINITION",
                        default=None,
                        nargs="?",
                        help="Environment definition")

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        default=False,
                        help="Show verbose output")

    parser.add_argument("--no-parallel",
                        dest="parallel",
                        action="store_false",
                        default=True,
                        help="Disable parallel processing")

    parser.add_argument("-d", "--define",
                        dest="defines",
                        action="append",
                        default=[],
                        help="Define local variables")
    return parser, subparsers


def init_cli_args_parser(ext_mgr):
    parser, subparsers = cli_arg_parser(ext_mgr)
    commands = ext_mgr.get_commands()

    for command in map(lambda c: c["class"], commands):
        sub_parser = subparsers.add_parser(command.name, help=command.help)
        command.argument_parser(sub_parser)

    return parser


def init_config(store):
    store.set("runtime/config", paths.local("config.yml"))

    # load defaults / home configuration into variable store
    config = util.yaml_read(store.get("runtime/config"))
    store.set("global", config)


def init_defines(store, args):
    # merge with arguments from commandline
    for define in [d.split("=") for d in args.defines]:
        if len(define) != 2:
            warn("Invalid variable definition detected")
            warn("Use -Dscope/variable=value")
            return 1
        store.set(define[0], util.convert_type(define[1]))

    # merge with arguments from environment
    for envvar in filter(lambda x: x.startswith("XII_"), os.environ):
        store.set(envvar[4:], os.environ[envvar])


def init_cli_settings(store, args):
    store.set("global/parallel", args.parallel)
    store.set("global/verbose", args.verbose)
    store.set("command", vars(args))


def init_command(store, cli_args, ext_mgr):
    command = ext_mgr.get_command(cli_args.command)

    if command is None:
        raise Bug("Could not find command implementation for '{}'"
                  .format(cli_args.command))

    if command["class"].require_definition:
        store.set("runtime/definition",
                  util.find_definition_file(cli_args.definition))

        # parse definition file
        defn = util.jinja_read(store.get("runtime/definition"), store)

        # construct component configurations
        definition.prepare_store(defn, store)

    instance = command["class"](cli_args, command["templates"], store)

    if command["class"].require_definition:
        prepare_command_instance(instance, ext_mgr)

    return instance


def run_cli():
    try:

        # load all components
        ext_mgr = ExtensionManager()
        ext_mgr.add_builtin_path()
        ext_mgr.load()

        # prepare local environment xii runs in
        paths.prepare_local_paths()

        # load variable store
        store = Store()

        # parse cli arguments
        parser = init_cli_args_parser(ext_mgr)
        cli_args = parser.parse_args()

        # initialize store and command
        init_config(store)
        init_defines(store, cli_args)
        init_cli_settings(store, cli_args)
        cmd = init_command(store, cli_args, ext_mgr)

        return cmd.run()

    except Interrupted:
        warn("interrupted... stopping immediately!")
        return 1

    except XiiError as e:
        it = iter(e.error())
        warn(e.error_title() + ": " + next(it))

        for line in it:
            warn(line)

        return 1
