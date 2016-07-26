from xii import component, attribute, util
from xii.output import debug


# Load all modules in components/ subdirectory
__all__ = util.load_modules(__path__)


def from_definition(dfn, conf, conn):
    cmpnts = []
    for name, settings in dfn.items():
        cmpnts.append(_create_component(settings, name, conn, conf))
    return cmpnts


def get(dfn, name, conn, conf):
    settings = dfn.item(name)
    if not settings:
        return None
    return _create_component(settings, name, conn, conf)


def _create_component(settings, name, conn, conf):
    cmpnt = component.Register.get(settings['type'])(name, conn, conf)

    cmpnt.add_default_attributes()

    for attr_name, attr_settings in settings.items():
        if attr_name in ['type']:
            continue

        attr = attribute.Register.get(attr_name)

        if not attr:
            debug("Unkown attribute `{}`. Skipping.".format(attr_name))
            continue
        cmpnt.add_attribute(attr_name, attr(attr_settings, cmpnt))

    # check if component is correctly initialized
    cmpnt.is_ready()
    return cmpnt
