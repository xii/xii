import re

import libvirt

from xii import error
from xii.output import debug, warn


def establish(dfn, conf):
    return Connection(dfn, conf)


class Connection():
    def __init__(self, dfn, conf):

        uri = dfn.settings('connection', conf.default_host())


        self.uri = uri
        self.dfn_file = dfn.file_path()
        self.config = conf
        self.hypervisor = 'qemu'
        self.is_local = True
        self.user = None
        self.host = None
        self.domain = 'session'
        self.libvirt = None

        self.parse_uri(uri)

    def parse_uri(self, uri):
        matcher = re.compile(r'([a-z]+)(\+([a-z]+))?:\/\/\/([a-z.]+)(@([a-z0-9.]+)\/([a-z]+))?')
        matched = matcher.match(uri)
        if not matched:
            raise error.ParseError(self.dfn_file, "Invalid connection URL specified")

        # NOTE: Currently only qemu is supported
        if matched.group(1) != 'qemu':
            raise RuntimeError("Currently only qemu is supported.")

        self.domain = matched.group(4)
        if matched.group(3) == 'ssh':
            self.is_local = False
            self.user = matched.group(4)
            self.host = matched.group(6)
            self.domain = matched.group(7)


    def virt(self):
        def error_handler(_, err):
            if err[3] != libvirt.VIR_ERR_ERROR:
                warn("Non-error from libvirt: '{}'".format(err[2]))

        if self.libvirt:
            return self.libvirt

        libvirt.registerErrorHandler(f=error_handler, ctx=None)

        self.libvirt = libvirt.open(self.uri)

        if not self.libvirt:
            raise error.LibvirtError("Could not connection to `{}`".format(self.uri))
        return self.libvirt


 
    def run(self, command):
        if self.is_local:
            debug("[local] " + command)
        else:
            debug("[remote] " + command)
