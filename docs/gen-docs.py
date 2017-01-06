import os
import jinja2
import shutil
from functools import partial

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


def item(item, action):
    pad = 15
    fill = pad - len(item)
    print("{}{} {}".format(item, " " * fill, action))

def text_if(maybe_text, replace=""):
    if maybe_text is None:
        return replace
    return maybe_text


def text_block_if(maybe_text):
    return text_if(maybe_text, no_text)


def generate_category(category, items, generator):
    print("GENERATE " + (category + "s").upper())
    dir = relative(category + "s")
    single_tpl = load_template(category + ".rst.tpl")
    overview_tpl = load_template(category + "s.rst.tpl")
    overview_toc = []

    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)

    if os.path.exists(relative(category + "s.rst")):
        os.remove(relative(category + "s.rst"))
    for i in [i["class"] for i in items]:
        name = generator(i, single_tpl)
        item(name, "generated")
        overview_toc.append(os.path.join(category + "s", name))

    save_file(relative(category + "s.rst"), overview_tpl.render({
        "toc": overview_toc
    }))
    item(category + " index", "generated!")


# generator ------------------------------------------------------------------

def generate_command(command, tpl):
    commandline = command.argument_parser().format_help().split("\n")
    help = text_if(command.help)
    description = text_block_if(command.__doc__)

    name = command.name[0]
    for n in command.name:
        if len(n) > name:
            name = n


    save_file("commands/{}.rst".format(name), tpl.render({
        "name": name,
        "help": help,
        "description": description,
        "commandline": commandline
    }))
    return name

def generate_component(ext_mgr, component, tpl):
    component_path = relative("components", component.ctype)
    print(" component path = {}".format(component_path))

    doc = text_block_if(component.__doc__)
    short_desc = text_if(component.short_description)
    toc = []

    # prepare directory
    os.mkdir(component_path)
    os.mkdir(os.path.join(component_path, component.ctype))

    attributes = [a["class"] for a in ext_mgr.get_attributes(component.ctype)]
    attribute_tpl = load_template("attribute.rst.tpl")

    for attr in attributes:
        item(" :: " + attr.atype, "generating...")
        name = generate_attribute(component.ctype, attr, attribute_tpl)
        toc.append(os.path.join(component_path, component.ctype, name))

    save_file("components/{}.rst".format(component.ctype), tpl.render({
        "name": component.ctype,
        "require_components": component.requires,
        "require_attributes": component.required_attributes,
        "short_desc": short_desc,
        "doc": doc,
        "toc": toc
    }))

    return component.ctype

def generate_attribute(component, attribute, tpl):
    save_file("components/{}/{}.rst".format(component, attribute.atype), tpl.render({
        "name": attribute.atype
    }))
    return attribute.atype


# Main ------------------------------------------------------------------------

def main():
    ext_mgr = ExtensionManager()
    ext_mgr.add_builtin_path()
    ext_mgr.load()

    generate_category("command", ext_mgr.get_commands(), generate_command)
    generate_category("component", ext_mgr.get_components(), partial(generate_component, ext_mgr))

if __name__ == "__main__":
    main()
