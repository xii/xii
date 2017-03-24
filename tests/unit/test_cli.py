from pytest import raises

from xii import cli
from xii.extension import ExtensionManager

# test ext_mgr
ext_mgr = ExtensionManager()
ext_mgr.add_builtin_path()
ext_mgr.load()


class FakeRegisterAvailable():
    def __init__(self, commands):
        self._commands = commands

    def available(self):
        return self._commands


def test_usage_text():
    result = cli.usage_text(ext_mgr)

    assert("xii [OPTIONS]" in result)
    assert("Commands available:" in result)
    assert("d        destroy" in result)
    assert("s        start" in result)


def test_cli_arg_parser():
    parser = cli.cli_arg_parser(ext_mgr)

    result = parser.parse_args([
        "--no-parallel",
        "--deffile", "/tmp/xii/config",
        "-Dtest=true", "-D", "foo=bar",
        "start",
        "foo"
    ])

    assert(result.parallel is False)
    assert(result.deffile == "/tmp/xii/config")
    assert(result.defines == ["test=true", "foo=bar"])
    assert(result.command == "start")
    assert(result.command_args == ["foo"])



def test_run_cli(monkeypatch, capsys):
    pass
