import os
import jinja2
import shutil

from xii.extension import ExtensionManager

no_text = ("This part is currently undocumented.\n\n"
           "Help us to make the documentation more complete and add "
           "informations here. \n\n"
           "Check #url for more information!")


# Util ------------------------------------------------------------------------

def relative(*path):
    return os.path.join(os.path.dirname(__file__), *path)


def load_template(filename):
    extpath, name = os.path.split(filename)
    path = relative("templates", extpath)
    from_file = jinja2.FileSystemLoader(path)
    env = jinja2.Environment(loader=from_file,
                             trim_blocks=True,
                             lstrip_blocks=True,
                             undefined=jinja2.StrictUndefined)
    return env.get_template(name)


def save_file(filename, content):
    if not os.path.isabs(filename):
        relative(filename)
    with open(filename, 'w+') as hdl:
        hdl.seek(0)
        if isinstance(content, list):
            hdl.write("\n".join(content))
        else:
            hdl.write(content)
        hdl.truncate()


def section(section):
    stop = 50
    fill = stop - len(section)
    print("[{}] {}".format(section, "-" * fill))


def item(item, action):
    pad = 15
    fill = pad - len(item)
    print("{}{} {}".format(item, " " * fill, action))


def note(msg):
    print(msg)

def text_if(maybe_text, replace=""):
    if maybe_text is None:
        return replace
    return maybe_text


def text_block_if(maybe_text):
    text_if(maybe_text, no_text)


# Commands --------------------------------------------------------------------

def generate_commands(ext_mgr):
    section("CREATE COMMANDS")
    commands = ext_mgr.get_commands()
    commands_dir = relative("commands")
    command_tpl = load_template("command.rst.tpl")
    commands_tpl = load_template("commands.rst.tpl")
    commands_toc = []

    if os.path.exists(commands_dir):
        shutil.rmtree(commands_dir)
        os.mkdir(commands_dir)

    if os.path.exists(relative("commands.rst")):
        os.remove(relative("commands.rst"))

    for command in [c["class"] for c in commands]:
        name = generate_command(command, command_tpl)
        item(name, "generated")
        commands_toc.append(os.path.join("commands", name))

    save_file(relative("commands.rst"), commands_tpl.render({
        "toc": commands_toc
    }))
    item("command index", "generated!")


def generate_command(command, tpl):
    help = text_if(command.help)
    description = text_block_if(command.__doc__)

    name = command.name[0]
    for n in command.name:
        if len(n) > name:
            name = n

    save_file("commands/{}.rst".format(name), tpl.render({
        "name": name,
        "help": help,
        "description": description
    }))
    return name


# Main ------------------------------------------------------------------------

def main():
    ext_mgr = ExtensionManager()
    ext_mgr.add_builtin_path()
    ext_mgr.load()

    generate_commands(ext_mgr)

    




if __name__ == "__main__":
    main()
