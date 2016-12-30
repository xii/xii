from abc import ABCMeta, abstractmethod

from xii import attribute, need


class PoolAttribute(attribute.Attribute, need.NeedLibvirt):
    # Every attribute needs to set this
    pool_type = None

    def get_tmp_volume_path(self):
        return self.other_attribute("image").get_tmp_volume_path()

    def add_xml(self, xml):
        self.parent().add_xml(xml)
