import os

from threading import Lock
from abc import ABCMeta, abstractmethod


# synchronize output from multiple threads
output_lock = Lock()


class colors:
    TAG = '\033[0m'
    NORMAL = '\033[37m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WARN = '\033[91m'
    SUCCESS = '\033[34m'


def width():
    # FIXME: port me to subprocess
    _, columns = os.popen('stty size', 'r').read().split()
    return int(columns)


def warn(msg, tag="[xii]"):
    output = "{} {}".format(tag, msg)
    print(colors.WARN + colors.BOLD + output + colors.CLEAR)


class HasOutput:
    __meta__ = ABCMeta

    @abstractmethod
    def entity_path(self):
        pass

    def say(self, msg):
        self._tprint(self._generate_tag(),
                     msg,
                     colors.NORMAL)

    def counted(self, i, msg):
        tag = "{}[#{}]".format(self._generate_tag(), i)
        self._tprint(tag,
                     msg,
                     colors.NORMAL)

    def warn(self, msg):
        self._tprint(self._generate_tag(),
                     msg,
                     colors.WARN + colors.BOLD)

    def success(self, msg):
        self._tprint(self._generate_tag(),
                     msg,
                     colors.SUCCESS + colors.BOLD)

    def _tprint(self, tag, msg, wrap=None):
        stop = 35
        fill = stop - len(tag)
        line = "{} {}: {}".format(tag, "." * fill, msg)

        if wrap:
            line = wrap + line + colors.CLEAR
        output_lock.acquire()
        print(line)
        output_lock.release()

    def _generate_tag(self):
        tag = ""
        for ident in self.entity_path()[1:]:
            tag += "[" + ident + "]"
        return tag
