from xii import error, paths
from xii.attribute import Attribute
from xii.validator import Dict, Key, String, Required, Or
from xii.output import show_setting


class ModeAttribute(Attribute):
    attr_name = "mode"
    allowed_components = "network"
    defaults = {
        'type': 'nat'
    }

    keys = Or([
        String(),
        Dict([
            Required(Key('type', String())),
            Required(Key('dev', String()))
            ])
        ])

    def info(self):
        if self.settings:
            state = self.settings['type']

            if self.settings['type'] == 'route' and 'dev' in self.settings:
                state += " (" + self.settings['dev'] + ")"
            show_setting('mode', state)

    def validate_settings(self):
        Attribute.validate_settings(self)

        if self.settings['type'] not in ['nat', 'route']:
            raise error.DefError("Unknown network mode '{}'".format(self.settings['type']))

    def spawn(self):
        template = 'mode.xml'

        if self.settings['type'] == "route" and 'dev' in self.settings:
            template = 'mode_route_dev.xml'

        xml = paths.template(template)
        self.cmpnt.add_xml(xml.safe_substitute(self.settings))


ModeAttribute.register()
