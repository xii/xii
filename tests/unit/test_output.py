import io
from pytest import raises, fail

from xii import output


def test_width(monkeypatch):
    stty_size = io.StringIO(u"32 144")

    def _fake_popen(cmd, mode):
        if cmd != "stty size":
            fail("invalid command was called with popen")
        return stty_size

    monkeypatch.setattr("os.popen", _fake_popen)

    assert(output.width() == 144)


def test_warn(capsys):
    output.warn("test")

    out, _ = capsys.readouterr()

    assert('[xii] test' in out)


class TestHasOutput(output.HasOutput):
    def entity_path(self):
        return ["test", "hasOutput"]

def test_generate_tag():
    test = TestHasOutput()

    assert(test._generate_tag() == "[test][hasOutput]")

def test_tprint(capsys):
    test = TestHasOutput()

    # non wrapped
    test._tprint("[test]", "12345", wrap=None)
    tag = "[test] " + ("." * 29)

    out, _ = capsys.readouterr()

    assert(tag in out)
    assert("12345" in out)

    # wrapped
    test._tprint("[test]", "12345", wrap="x")
    tag = "x[test] " + ("." * 29)

    out, _ = capsys.readouterr()

    assert(tag in out)


def test_output(capsys):
    test = TestHasOutput()

    def stdout():
        out, _  = capsys.readouterr()
        return out

    # say
    test.say("Normal text")
    assert("Normal text" in stdout())

    # counted
    test.counted(12, "Counted text")
    out = stdout()
    assert("[#12]" in out)
    assert("Counted text" in out)

    # warn
    test.warn("Warn text")
    out = stdout()
    assert(output.colors.WARN + output.colors.BOLD in out)
    assert("Warn text" in out)

    #success
    test.success("Success text")
    out = stdout()
    assert(output.colors.SUCCESS + output.colors.BOLD in out)
    assert("Success text" in out)
