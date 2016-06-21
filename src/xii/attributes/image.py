import os

from xii import attribute, paths


class ImageAttribute(attribute.Attribute):
    name = "image"
    allowed_components = "node"

    def start(self):
        self.parse_source()
        if not self.storage_exists():
            self.prepare_storage()

        if not self.image_exists():
            self.prepare_image()

        self.clone_image_to_storage()

        self.cmpnt.add_xml(self.gen_xml())

    def parse_source(self):
        self.local_image = True
        self.name = os.path.basename(self.settings)

        parsed = urlparse.urlparse(self.settings)

        # Local file
        if parsed.scheme == "":
            return

        # Http based download
        if parsed.scheme in ["http", "https"]:
            self.local_image = False
            return

        raise error.InvalidSource("Not supported image "
                                  "location: {}".format(self.settings))

    def storage_path(extend=None):
        storage = paths.storage_path(self.conn().get_user_path())

        if extend:
            return os.path.join(storage, extend)
        return storage

    def storage_exists(self):
        path = self.storage_path('images')
        return self.conn().isdir(path)

    def image_exists(self):
        path = self.storage_path('images/' + self.

        conn = self.cmpnt.conn

        storage = paths.storage_path(conn.get_
        pass

    def prepare_image(self):
        pass

    def clone_image_to_storage(self):
        pass

    def gen_xml(self):
        pass


attribute.Register.register('image', ImageAttribute)
