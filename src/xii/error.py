
class FileError(RuntimeError):
    def __init__(self, file, msg):
        RuntimeError.__init__(self, "File error: {}. "
                                    "\n\n(file was: {})".format(msg, file))


class ParseError(RuntimeError):
    def __init__(self, file, msg):
        RuntimeError.__init__(self, "Could not parse file: {}. "
                                    "\n\n(file was: {})".format(msg, file))


class InvalidSettings(RuntimeError):
    def __init__(self, typ, msg):
        RuntimeError.__init__(self, "Invalid configuration in {}: {} ".format(typ, msg))


class InvalidAttribute(RuntimeError):
    def __init__(self, file, prop, invalid):
        RuntimeError.__init__(self, "Attribute `{}` is invalid (unknown value: {}) "
                                    "\n\n(file was: {})".format(prop, invalid, file))


class Bug(RuntimeError):
    def __init__(self, file, msg):
        RuntimeError.__init__(self, "BUG: {}. This indicates there is something "
                                    "terrible wrong.\nIf you nice, please report this "
                                    "to the github issue tracker. "
                                    "\n\n(file was: {})".format(msg, file))


class InvalidSource(RuntimeError):
    pass


class LibvirtError(RuntimeError):
    def __init__(self, err, msg=""):
        RuntimeError.__init__(self, "Libvirt action failed: {}.\n\n{}".format(msg, err))

class DoesNotExist(RuntimeError):
    pass

class SSHError(RuntimeError):
    pass
