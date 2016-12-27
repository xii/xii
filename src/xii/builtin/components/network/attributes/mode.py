from xii import error, paths
from xii.attribute import Attribute
from xii.validator import Dict, Key, String, Required, Or

from base import NetworkAttribute


class ModeAttribute(NetworkAttribute):
    atype = "mode"

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

    def validate_settings(self):
        Attribute.validate_settings(self)

        if self._get_mode() not in ['nat', 'route']:
            raise error.DefError("Unknown network mode '{}'".format(self._get_mode()))

    def spawn(self):
        template = 'mode.xml'

        if self._get_dev():
            template = 'mode_route_dev.xml'

        xml = paths.template(template)
        self.add_xml(xml.safe_substitute({
            'type': self._get_mode(),
            'dev': self._get_dev()
        }))

    def _get_mode(self):
        if isinstance(self.settings(), dict):
            return self.settings('type')
        return self.settings()

    def _get_dev(self):
        if isinstance(self.settings(), dict):
            return self.settings('dev')
        return None


ModeAttribute.register()
