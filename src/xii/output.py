import os
import sys

from abc import ABCMeta, abstractmethod

OUTPUT_VERBOSE = False


def set_verbose():
    global OUTPUT_VERBOSE
    OUTPUT_VERBOSE = True


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


class HasOutput():
    __metaclass__ = ABCMeta

    _infos = {}

    @abstractmethod
    def ident(self):
        pass

    def add_info(self, key, value):
        self._infos[key] = value

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


    def show_info(self, msg):
        self.say(msg)
        for key, key in self._infos.items():
            if isinstance(key, list):
                print(sep("{:25}: {}".format(key, key[0])))
                for line in key[1:]:
                    print(sep("{:25}    {}".format("", line)))
            else:
                print(sep("{:25}: {}".format(key, key)))


    def _generate_tag(self):
        tag = ""
        for i in self.ident():
            tag += "[" + i + "]"
        return tag


def terminal_columns():
    _, columns = os.popen('stty size', 'r').read().split()
    return int(columns)


def width():
    columns = terminal_columns()
    return int(columns - (columns * 0.25))


def progress(message, current, full):
    perc = int(100 * (float(current) / full))
    sys.stdout.write("\r{}".format(sep(":: {} {}%...".format(message, perc))))
    if perc > 99:
        sys.stdout.write("\n")
    sys.stdout.flush()


def show_setting(key, value):
    if isinstance(value, list):
        print(sep("{:25}: {}".format(key, value[0])))
        for line in value[1:]:
            print(sep("{:25}    {}".format("", line)))
    else:
        print(sep("{:25}: {}".format(key, value)))


def hr(msg):
    return msg + '=' * (width() - len(msg))


def header(msg):
    print(colors.HEADER + colors.BOLD + hr(msg + " ") + colors.CLEAR)


def section(msg):
    print(colors.SECTION + "  ===> " + msg + colors.CLEAR)


def sep(msg, sep=0):
    return " " * (2 + sep) + msg


def fatal(msg):
    print(colors.FATAL + colors.BOLD + msg + colors.CLEAR)


def info(msg, ext=0):
    print(sep(">> " + msg, ext))


def warn(msg):
    print(colors.WARNING + sep(msg) + colors.CLEAR)


def debug(msg):
    if OUTPUT_VERBOSE:
        print(msg)
