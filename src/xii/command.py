

class CommandRegister(object):
    registered = []

    @classmethod
    def get(cls, settings):
        for command in cls.registered:
            if settings.name in command.name:
                return command(settings.args)
        return None

    @classmethod
    def available(cls):
        output = []
        for command in cls.registered:
            output.append(', '.join(command.name) + "    " + command.help)
        return output

    @classmethod
    def register(cls, command):
        cls.registered.append(command)


class Command():
    name = ["invalidcommand"]
    help = "No help given"

    def __init__(self, args=[]):
        self.args    = args

    def run(self):
        raise RuntimeError("run() is not implemeted")
