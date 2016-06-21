from xii import component, attribute, util
from xii.output import debug


# Load all modules in components/ subdirectory
__all__ = util.load_modules(__path__)


def from_definition(dfn, conf, conn):
    cmpnts = []
    for name, settings in dfn.items():
        cmpnt = component.Register.get(settings['type'])(name, conn, conf)

        for attr_name, attr_settings in settings.items():
            if attr_name in ['type']:
                continue

            attr = attribute.Register.get(attr_name)

            if not attr:
                debug("Unkown attribute `{}`. Skipping.".format(attr_name))
                continue
            cmpnt.add_attribute(attr(attr_settings, cmpnt))
        cmpnts.append(cmpnt)
    return cmpnts
