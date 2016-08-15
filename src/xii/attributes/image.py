import os
import subprocess
import stat

from urllib2 import urlparse

from xii import paths, error
from xii.need import NeedIO, NeedLibvirt
from xii.attribute import Attribute
from xii.validator import String


class ImageAttribute(Attribute, NeedIO, NeedLibvirt):
    entity = "image"

    needs = ["node"]

    keys = String()

    def get_storage_path(self):
        return paths.storage_path(self.io().user_home())

    def get_image_path(self):
        return os.path.join(self.get_storage_path(), "images/" + self.image_name)

    def get_domain_image_path(self):
        image_file = self.component_name() + ".qcow2"
        return os.path.join(self.get_storage_path(), 'storage/' + image_file)


    def __init__(self, value, cmpnt):
        Attribute.__init__(self, value, cmpnt)
        self.image_name = os.path.basename(self.settings)


    def prepare(self):
        self.add_info("image", self.image_name)

    def spawn(self):
        self._parse_source()
        self._prepare_storage()
        self._prepare_pool()

        # download/copy image to storage
        if not self.io().exists(self.get_image_path()):
            self._prepare_image()

        # clone image for explicit domain
        if not self.io().exists(self.get_domain_image_path()):
            self.say("cloning image...")
            self.io().copy(self.get_image_path(), self.get_domain_image_path())
            self.io().chmod(self.get_domain_image_path(), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR, append=True)
            self.io().chmod(self.get_domain_image_path(), stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH, append=True)

        self.get_parent().add_xml('devices', self._gen_xml())

    def destroy(self):
        if self.io().exists(self.get_domain_image_path()):
            self.io().remove(self.get_domain_image_path())


    def _parse_source(self):
        self.local_image = True

        parsed = urlparse.urlparse(self.settings)

        # Local file
        if parsed.scheme == "":
            return

        # Http based download
        if parsed.scheme in ["http", "https"]:
            self.local_image = False
            return

        raise error.DefError("Not supported image "
                             "location: {}".format(self.settings))

    # set selinux permissions
    def _fix_permissions(self):
        user = self.io().user()
        storage = os.path.join(self.get_storage_path(), 'storage')

        cmd = ["setfacl", "--modify", "user:{}:x".format(user), storage]
        setfacl = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        _, err = setfacl.communicate()

        self.io().chmod(storage, stat.S_IXOTH, append=True)

        if setfacl.returncode != 0:
            raise PermissionError(storage, err)


    # prepare storage location
    # currently: ~/.local/share/xii/storage (running instances)
    #            ~/.local/share/xii/images (already stored images)
    def _prepare_storage(self):
        storage = os.path.join(self.get_storage_path(), 'storage')
        images = os.path.join(self.get_storage_path(), 'images')

        if not self.io().exists(storage):
            self.io().mkdir(storage, recursive=True)

        if not self.io().exists(images):
            self.io().mkdir(images)

    # setup a new pool if not already existing
    def _prepare_pool(self):
        pool = self.get_pool('xii')

        if not pool:
            self.say("local storage pool does not exist. Creating a new one")
            xml = paths.template('pool.xml')
            self.virt().storagePoolDefineXML(xml.safe_substitute({'storage': self.get_storage_path() + '/storage'}))

            # Add access rights
            self._fix_permissions()

            pool = self.io().get_pool('xii')
            pool.setAutostart(True)

        if not pool.isActive():
            pool.create()

    def _prepare_image(self):
        self.say("importing {}...".format(self.image_name))
        if self.local_image:
            self.io().copy(self.settings, self.get_image_path())
        else:
            self.io().download(self.settings, self.get_image_path())

    def _gen_xml(self):
        xml = paths.template('disk.xml')
        return xml.safe_substitute({'image': self.get_domain_image_path()})


ImageAttribute.register()
