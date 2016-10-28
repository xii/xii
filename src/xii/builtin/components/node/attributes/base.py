from xii import attribute, entity, need


class NodeAttribute(attribute.Attribute, need.NeedLibvirt):

    @classmethod
    def register(cls):
        entity.EntityRegister.register_attribute("node", cls)

    def get_tmp_volume_path(self):
        return self.other_attribute("image").get_tmp_volume_path()

    def add_xml(self, section, xml):
        self.parent().add_xml(section, xml)

    def default_ssh_connection(self):
        user     = self.get("settings/user", self.other_attribute("user").default_user())
        host     = self.get("settings/host", self.domain_get_ip(self.component_entity()))
        password = self.get("settings/password", None)
        key      = self.get("settings/keyfile", None)
        return (user, host, password, key)
