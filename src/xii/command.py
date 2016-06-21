class Register(object):
    registered = []

    @classmethod
    def get(cls, name, args, conf):
        for command in cls.registered:
            if name in command.name:
                return command(args, conf)
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

    def __init__(self, args, conf):
        self.args = args
        self.conf = conf

    def run(self):
        pass
