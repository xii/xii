from pytest import raises

from xii import cli


class FakeRegisterAvailable():
    def __init__(self, commands):
        self._commands = commands

    def available(self):
        return self._commands


def test_usage_text(monkeypatch):
    monkeypatch.setattr("xii.command.Register", FakeRegisterAvailable(["command1, command2"]))

    result = cli.usage_text()

    assert("xii [OPTIONS]" in result)
    assert("Commands available:" in result)
    assert("command1, command2" in result)


def test_cli_arg_parser():
    parser = cli.cli_arg_parser()

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
