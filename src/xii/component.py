from abc import ABCMeta, abstractmethod

from xii.entity import Entity
from xii.store import HasStore
from xii import error, util


class Component(Entity, HasStore):
    __metaclass__ = ABCMeta

    ctype = ""
    """
    Name of the component (eg. 'node')
    """

    default_attributes = []
    """
    List of default attributes which are created if not defined in a
    definition file
    """

    required_attributes = []
    """
    Required attributes for this component
    """

    short_description = None

    def __init__(self, name, command, tpls={}):
        self._meta = {}
        Entity.__init__(self, name, parent=command, templates=tpls)

    @abstractmethod
    def fetch_metadata(self):
        """fetch metadata from component
        This method needs to be implemented to make xii work properly.

        It should fetch the metadata and return them as dict.

        For each component must set the created_at metadata!

        If no metadata is available return None

        Returns:
            A dict of key value pairs or None if not available
        """
        pass

    def add_meta(self, key_or_dict, value=None):
        """add metadata to component

        Value is converted to string, make sure added values
        have a usefull __repr__ method.

        Key which have been already defined are overwritten.

        Args:
            key_or_dict : name for the metadata attribute or a dict to add
            value: value you want to set
        """
        if isinstance(key_or_dict, dict):
            self._meta.update(key_or_dict)
        else:
            self._meta[key_or_dict] = str(value)


    def meta_to_xml(self):
        """get a xml representation for the metadata

        This function can be used to add metadata to libvirt based
        components more easy.

        Returns:
            The xml created or an empty string if no meta data was added
        """
        if not len(self._meta):
            return ""

        url = "https://xii-project.org/xmlns/" + self.ctype + "/1.0"
        attrs = reduce(lambda m, (k,v): m + util.create_xml_node(k, text=v),
                       self._meta.iteritems(),
                       "")

        return util.create_xml_node("xii:" + self.ctype,
                                    {"xmlns:xii": url},
                                    attrs)

    def get_virt_url(self):
        return self.get("host", "qemu:///system")

    # limit access to component/type/concret_instance
    def store(self):
        """get the store

        Returns:
            The store with lens to this components settings
        """
        path = "components/{}/{}".format(self.ctype, self.entity())
        return self.parent().store().derive(path)

    def command(self):
        """get owning command

        Returns:
            The command which this component is associated with
        """
        return self.parent()

    def attributes(self):
        """get all attributes

        Returns:
            A list of all already added attributes
        """
        return self._childs

    def add_attribute(self, attribute):
        """add a new attribute

        Args:
            attribute: Attribute object to add
        """
        return self.add_child(attribute)

    def each_attribute(self, action, reverse=False):
        """run a action on each attribute

        ::
            self.each_attribute("start")
            # reverse order
            self.each_attribute("stop", reverse=True)

        Args:
            action: Action which should be executed
            reverse: Run the action in reversed order
        """
        return self.each_child(action, reverse)

    def get_attribute(self, name):
        """get added attribute

        Returns:
            Attribute object or None if not found
        """
        return self.get_child(name)

    def has_attribute(self, name):
        """check if component has attribute

        Returns:
            True if found or False
        """
        return not self.get_child(name) is None

    def get_temp_path(self, *args):
        """get the template path for this component

        All arguments are joined to one path

        Returns:
            Path to the template directory or file
        """
        return self.command().get_temp_path(self.entity(), *args)

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def validate(self):
        Entity.validate(self, self.required_attributes)


def from_definition(definition, command, ext_mgr):
    for component_type in definition:
        for name in definition[component_type].keys():
            cmpnt = ext_mgr.get_component(component_type)

            if not cmpnt:
                raise error.NotFound("Could not find component type {}!"
                                     .format(component_type))
            instance = cmpnt["class"](name, command, cmpnt["templates"])
            _initialize_attributes(instance, ext_mgr)

            yield instance


def _initialize_attributes(instance, ext_mgr):
    non_attributes = ["count", "type", "settings", "basename", "host"]

    def add_attr(name):
        attr = ext_mgr.get_attribute(instance.ctype, name)

        if not attr:
            raise error.NotFound("Invalid attribute `{}` for component "
                                 "{}. Maybe Missspelled?"
                                 .format(name, instance.entity()))

        instance.add_attribute(attr["class"](instance, attr["templates"]))

    # load defined attributes
    for n in instance.store().values().keys():
        if n not in non_attributes:
            add_attr(n)

    # add defaults
    for name in instance.default_attributes:
        if not instance.has_attribute(name):
            add_attr(name)

    # check if all required attributes are set
    for name in instance.required_attributes:
        if not instance.has_attribute(name):
            raise error.NotFound("{} needs a {} attribute but not found, "
                                 "add one!".format(instance.ctype, name))
