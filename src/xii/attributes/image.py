import os
import subprocess
import stat

from urllib2 import urlparse

from xii import attribute, paths, error
from xii.output import info, show_setting


class ImageAttribute(attribute.Attribute):
    name = "image"
    allowed_components = "node"

    def __init__(self, value, cmpnt):
        attribute.Attribute.__init__(self, value, cmpnt)
        self.local_image = False
        self.image_name = os.path.basename(self.value)
        self.storage_path = paths.storage_path(self.conn().user_home())
        self.storage_image = os.path.join(self.storage_path, 'images/' + self.image_name)
        self.storage_clone = None

    def info(self):
        show_setting('image', self.image_name)

    def spawn(self, domain_name):
        self.storage_clone = os.path.join(self.storage_path, 'storage/' + domain_name + '.qcow2')

        self._parse_source()
        self._prepare_storage()
        self._prepare_pool()

        if not self.conn().exists(self.storage_image):
            self._prepare_image()

        if not self.conn().exists(self.storage_clone):
            self.conn().copy("Clone image", self.storage_image, self.storage_clone)
            self.conn().chmod(self.storage_clone, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR, append=True)
            self.conn().chmod(self.storage_clone, stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH, append=True)

        self.cmpnt.add_xml('devices', self._gen_xml())

    def destroy(self, domain_name):
        self.storage_clone = os.path.join(self.storage_path, 'storage/' + domain_name + '.qcow2')

        if self.conn().exists(self.storage_clone):
            self.conn().remove(self.storage_clone)

    def clone(self, domain_name):
        return os.path.join(self.storage_path, 'storage/' + domain_name + '.qcow2')

    def _parse_source(self):
        self.local_image = True

        parsed = urlparse.urlparse(self.value)

        # Local file
        if parsed.scheme == "":
            return

        # Http based download
        if parsed.scheme in ["http", "https"]:
            self.local_image = False
            return

        raise error.InvalidSource("Not supported image "
                                  "location: {}".format(self.value))

    def _fix_permissions(self):
        user = self.conn().user()
        storage = os.path.join(self.storage_path, 'storage')

        cmd = ["setfacl", "--modify", "user:{}:x".format(user), storage]
        setfacl = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        _, err = setfacl.communicate()

        self.conn().chmod(storage, stat.S_IXOTH, append=True)

        if setfacl.returncode != 0:
            raise PermissionError(storage, err)

    def _prepare_storage(self):
        storage = os.path.join(self.storage_path, 'storage')
        images = os.path.join(self.storage_path, 'images')

        if not self.conn().exists(storage):
            self.conn().mkdir(storage, recursive=True)

        if not self.conn().exists(images):
            self.conn().mkdir(images)

    def _prepare_pool(self):
        pool = self.conn().get_pool('xii')

        if not pool:
            info("Local storage pool does not exist. Creating...")
            xml = paths.template('pool.xml')
            self.virt().storagePoolDefineXML(xml.safe_substitute({'storage': self.storage_path + '/storage'}))

            # Add access rights
            self._fix_permissions()

            pool = self.conn().get_pool('xii')
            pool.setAutostart(True)

        if not pool.isActive():
            pool.create()

    def _prepare_image(self):
        if self.local_image:
            self.conn().copy("Copy {}".format(self.image_name),
                             self.value,
                             self.storage_image)
        else:
            self.conn().download("Downloading {}".format(self.image_name),
                                 self.value,
                                 self.storage_image)

    def _gen_xml(self):
        xml = paths.template('disk.xml')
        return xml.safe_substitute({'image': self.storage_clone})


attribute.Register.register('image', ImageAttribute)
