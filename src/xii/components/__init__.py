from xii import util
from xii.ui import warn
from xii.entity import EntityRegister


# Load all modules in components/ subdirectory
__all__ = util.load_modules(__path__)


def from_definition(runtime):
    cmpnts = []
    for name, settings in runtime['definition'].items():
        cmpnts.append(_create_component(settings, name, runtime))
    return cmpnts


def get(name, runtime):
    settings = runtime['definition'].item(name)
    if not settings:
        return None
    return _create_component(settings, name, runtime)


def _create_component(settings, name, runtime):
    component_type = settings["type"]
    component_class = EntityRegister.get_entity(component_type, "component")
    component = component_class(name, runtime)

    component.load_defaults()

    for attr_name, attr_settings in settings.items():
        if attr_name in ["type", "count"]:
            continue

        attr = EntityRegister.get_entity(attr_name, "attribute", component_type)

        if not attr:
            warn("Unkown attribute `{}`. Skipping.".format(attr_name))
            continue
        component.add(attr(attr_settings, component))

    # check if component is correctly initialized
    component.validate()
    return component
