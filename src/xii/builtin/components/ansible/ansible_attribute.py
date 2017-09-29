from xii import attribute

class AnsibleAttribute(attribute.Attribute):
    def get_virt_url(self):
        return self.component().get_virt_url()

    def get_tmp_volume_path(self):
        return self.other_attribute("image").get_tmp_volume_path()
