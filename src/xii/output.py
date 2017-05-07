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

    @abstractmethod
    def is_verbose(self):
        pass

    def verbose(self, msg):
        if self.is_verbose():
            self._tprint(self._generate_tag(),
                         msg,
                         colors.NORMAL)

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

    def show_table(self, columns, rows, spacing=8):
        """print a table

        Example:
        ::
            columns = ["component", "type", "uptime", "status"]

            data = [["mutiple-1", "node", "2 days", "running"],
                    ["mutiple-2", "node", "1 days", "running"],
                    ["mutiple-2", "node", "-", "stopped"],
                    ["test-network", "network", "50 days", "created"]]

            self.show_table(columns, data)

        Args:
            columns: A list of all columns names
            rows:    All data which should be displayed
            spacing: Spacing between each column
        """
        header = []
        data = []
        col_spacings = []

        # calculate spacing dependig on column width
        def spacings(col_index, data):
            data_len = len(str(data))
            return " " * (col_spacings[col_index] - data_len)

        # calculate required sizes
        for i, col in enumerate(columns):
            col_len = max(map(lambda r: len(str(r[i])), rows))
            if col_len < len(col):
                col_len = len(col)
            col_spacings.append(col_len)

        # create column header
        for i, col in enumerate(columns):
            header.append("{}{}".format(col.upper(), spacings(i, col)))

        # create table rows
        for row in rows:
            row_data = []
            for i, cell in enumerate(row):
                row_data.append("{}{}".format(cell, spacings(i, cell)))
            data.append(row_data)

        # print everthing
        output_lock.acquire()
        seperator = "{}".format(" " * spacing)
        print(seperator.join(header))
        for row in data:
            print(seperator.join(row))
        output_lock.release()

    def _tprint(self, tag, msg, wrap=None):
        stop = 40
        fill = stop - len(tag)
        line = "{} {}: {}".format(tag, "." * fill, msg)

        if wrap:
            line = wrap + line + colors.CLEAR
        output_lock.acquire()
        print(line)
        output_lock.release()

    def _generate_tag(self):
        tag = ""
        for ident in self.entity_path():
            tag += "[" + ident + "]"
        return tag
