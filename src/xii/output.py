import os
import sys

OUTPUT_VERBOSE = False


def set_verbose():
    global OUTPUT_VERBOSE
    OUTPUT_VERBOSE = True


class colors:
    HEADER = '\033[34m'
    SECTION = '\033[34m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FATAL = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def terminal_columns():
    _, columns = os.popen('stty size', 'r').read().split()
    return int(columns)


def width():
    columns = terminal_columns()
    return int(columns - (columns * 0.25))


def progress(message, full, current):
    perc = int(100 * (float(current) / full))
    sys.stdout.write("\r{}".format(sep(":: {} {}%...".format(message, perc))))
    if perc > 99:
        sys.stdout.write("\n")
    sys.stdout.flush()


def show_setting(key, value):
    key_max = 20
    print(sep("{}{}: {}".format(key, ' ' * (key_max - len(key)), value)))


def hr(msg):
    return msg + '=' * (width() - len(msg))


def header(msg):
    print(colors.HEADER + colors.BOLD + hr(msg + " ") + colors.CLEAR)


def section(msg):
    print(colors.SECTION + " ===> " + msg + colors.CLEAR)


def sep(msg):
    return "  " + msg


def fatal(msg):
    print(colors.FATAL + colors.BOLD + msg + colors.CLEAR)


def info(msg):
    print(sep(msg))


def warn(msg):
    print(colors.WARNING + sep(msg) + colors.CLEAR)


def debug(msg):
    if OUTPUT_VERBOSE:
        print(msg)
