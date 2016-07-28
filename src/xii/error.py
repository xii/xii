
def _to_list(string_or_list):
    if isinstance(string_or_list, basestring):
        return [string_or_list]
    return string_or_list


class XiiError(RuntimeError):
    title = "Unkown Error"

    def __init__(self, lines):
        self.lines = _to_list(lines)

    def error_title(self):
        return self.title

    def error(self):
        return self.lines


class ValidatorError(XiiError):
    title = "Xii definition error"
    pass


class DefError(XiiError):
    title = "Xii definition error"
    pass


class ExecError(XiiError):
    title = "Runtime Error"
    pass


class ConnError(XiiError):
    title = "Connection Error"
    pass


class NotFound(XiiError):
    title = "Not found"
    pass


class Bug(XiiError):
    title = "Bug"

    def __init__(self, message):
        XiiError.__init__(self, _to_list(message)
                                + ["This should never happen."]
                                + ["Please report this issue."])
