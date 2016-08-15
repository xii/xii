import os
import sys

from abc import ABCMeta, abstractmethod
from threading import Lock


class colors:
    TAG = '\033[34m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WARN = '\033[91m'
    SUCCESS = '\033[92m'

    HEADER = '\033[34m'
    SECTION = '\033[34m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FATAL = '\033[91m'


def width():
    _, columns = os.popen('stty size', 'r').read().split()
    return int(columns)


def warn(msg, tag="[xii]"):
    output = "{} {}".format(tag, msg)
    print(colors.WARN + colors.BOLD + output + colors.CLEAR)


class Progressbar():
    def __init__(self, ui, target, msg, full):
        self._ui = ui
        self._target = target
        self._msg = msg
        self._full = full
        self._current = 0

    def current(self):
        return self._current

    def full(self):
        return self._full

    def init(self):
        self.render()

    def done(self, msg):
        self._ui.remove_bar(self, self._target, msg)

    def render(self):
        bar_width = int(width() * 0.2)
        perc = int(self._current / (self._full / 100)) + 1
        chars = int((bar_width * perc) / 100)
        empty_chars = width - chars
        out = "[{}{}]{:>4}%".format("#" * chars, " " * empty_chars, perc)

        self._ui.line(self._target, "{:25} {}".format(self._msg, out))

    def update(self, state):
        self._current = state
        self._ui.render()


class UI():

    def __init__(self):
        self._bars = []
        #self.lock = Lock()

    def say(self, target, msg):
        #self.lock.acquire()

        self.up(len(self._bars))
        self.line(target, msg)
        self._render_bars()

        #self.lock.release()

    def progressbar(self, target, msg, full):
        #self.lock.acquire()
        pbar = Progressbar(self, target, msg, full)
        self._bars.append(pbar)
        pbar.render()
        self._render_bars()

        #self.lock.release()
        return pbar

    def remove_bar(self, remove, target, msg):
        #self.lock.acquire()

        self.up(len(self._bars))

        if remove in self._bars:
            self._bars.remove(remove)

        self.line(target, msg)

        self._render_bars()

        #self.lock.release()

    def render(self):
        self.lock.acquire()

        self._render_bars()

        self.lock.release()

    def clear(self):
        sys.stdout.write("\033[2K")
        sys.stdout.flush()

    def up(self, n):
        if n < 1:
            return
        sys.stdout.write("\033[{}F".format(n))
        sys.stdout.flush()

    def line(self, target, msg):
        full_width = width()
        out = "{:>20} {}".format(target, msg)
        print(out + " " * (full_width - len(out)))

    def _render_bars(self):
        self._update_bars()
        self.up(len(self._bars))
        for pbar in self._bars:
            pbar.render()

    def _update_bars(self):
        def get_state(pbar):
            return int(pbar.current() / (pbar.full() / 100)) + 1
        self._bars = list(reversed(sorted(self._bars, key=get_state)))


class HasOutput:
    __meta__ = ABCMeta

    @abstractmethod
    def get_ui(self):
        pass

    def say(self, msg):
        tag = colors.TAG + self._generate_tag() + colors.CLEAR
        print("{:30} {}".format(tag, msg))

    def add(self, msg, sp=0):
        self.say((" " * sp) + ":: " + msg)

    def warn(self, msg):
        output = "{:30} {}".format(self._generate_tag(), msg)
        print(colors.WARN + colors.BOLD + output + colors.CLEAR)

    def success(self, msg):
        output = "{:21} {}".format(self._generate_tag(), msg)
        print(colors.SUCCESS  + colors.BOLD + output + colors.CLEAR)

    def _generate_tag(self):
        tag = ""
        try:
            for ident in self.full_name():
                tag += "[" + ident + "]"
        except TypeError:
            import pdb; pdb.set_trace()
        return tag

