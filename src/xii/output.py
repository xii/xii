

OUTPUT_VERBOSE = False


def set_verbose():
    global OUTPUT_VERBOSE
    OUTPUT_VERBOSE = True


class colors:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FATAL = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fatal(msg):
    print(colors.FATAL + colors.BOLD + msg + colors.CLEAR)


def info(msg):
    print(colors.INFO + msg + colors.CLEAR)


def warn(msg):
    print(colors.WARNING + msg + colors.CLEAR)


def debug(msg):
    if OUTPUT_VERBOSE:
        print(msg)
