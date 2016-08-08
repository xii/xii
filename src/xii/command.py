class Register(object):
    registered = []

    @classmethod
    def get(cls, name, args, config, userinterface):
        for command in cls.registered:
            if name in command.name:
                return command(args, config, userinterface)
        return None

    @classmethod
    def available(cls):
        output = ["", "shortcut  action    description",
                  "-------------------------------"]
        for command in cls.registered:
            output.append(" {:9}{:10}{}".format(", ".join(command.name[1:]), command.name[0], command.help))
        output.append(" ")
        return output

    @classmethod
    def register(cls, command):
        cls.registered.append(command)


class Command():
    name = ["invalidcommand"]
    help = "No help given"

    def __init__(self, args, config, userinterface):
        self.args = args
        self.config = config
        self.userinterface  = userinterface

    def run(self):
        pass
