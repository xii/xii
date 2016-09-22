import io
from pytest import raises, fail

from xii import ui


def test_width(monkeypatch):
    stty_size = io.StringIO(u"32 144")

    def _fake_popen(cmd, mode):
        if cmd != "stty size":
            fail("invalid command was called with popen")
        return stty_size

    monkeypatch.setattr("os.popen", _fake_popen)

    assert(ui.width() == 144)


def test_warn(capsys):
    ui.warn("test")

    out, _ = capsys.readouterr()

    assert('[xii] test' in out)


class TestHasOutput(ui.HasOutput):
    def get_full_name(self):
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

    def output():
        out, _  = capsys.readouterr()
        return out

    # say
    test.say("Normal text")
    assert("Normal text" in output())

    # counted
    test.counted(12, "Counted text")
    out = output()
    assert("[#12]" in out)
    assert("Counted text" in out)

    # warn
    test.warn("Warn text")
    out = output()
    assert(ui.colors.WARN + ui.colors.BOLD in out)
    assert("Warn text" in out)

    #success
    test.success("Success text")
    out = output()
    assert(ui.colors.SUCCESS + ui.colors.BOLD in out)
    assert("Success text" in out)
