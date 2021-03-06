import os
import time
import hashlib

from multiprocessing import Condition

from xii import paths, error, need, util

from xii.attribute import Attribute
from xii.validator import String


_pending = Condition()


class ImageAttribute(Attribute, need.NeedIO, need.NeedLibvirt):
    atype = "image"

    requires = ['pool']
    keys = String("~/images/openSUSE-leap-42.2.qcow2")

    def get_virt_url(self):
        return self.component().get_virt_url()

    def get_tmp_volume_path(self):
        ext = os.path.splitext(self.settings())[1]
        return self.get_temp_path("image" + ext)

    def create(self):
        # create image store if needed
        self.io().ensure_path_exists(self._image_store_path())

        pool_name = self.other_attribute("pool").used_pool_name()
        # pool_type = self.other_attribute("pool").used_pool_type()

        volume = self.get_volume(pool_name,
                                 self.component_entity(),
                                 raise_exception=False)

        if volume:
            self._remove_volume(volume)

        if not self.io().exists(self._image_path()):
            self._fetch_image()
        self.verbose("image path = {}".format(self._image_path()))

        self.say("cloning image...")
        self.verbose("tmp_path = {}".format(self.get_tmp_volume_path()))
        self.io().copy(self._image_path(), self.get_tmp_volume_path())

    def after_spawn(self):
        pool = self.other_attribute("pool").used_pool()
        self.verbose("tmp_path = {}".format(self.get_tmp_volume_path()))
        size = self.io().stat(self.get_tmp_volume_path()).st_size
        volume_tpl = self.template("volume.xml")
        xml = volume_tpl.safe_substitute({
            "name": self.component_entity(),
            "capacity": size
            })

        # FIXME: Add error handling
        volume = pool.createXML(xml)

        self.say("importing...")
        self.io().call("virsh", "-c", "qemu:///system",
                       "vol-upload",
                       "--pool", pool.name(),
                       self.component_entity(),
                       self.get_tmp_volume_path())

        disk_tpl = self.template("disk.xml")
        xml = disk_tpl.safe_substitute({
            "pool": pool.name(),
            "volume": self.component_entity()
        })

        self.parent().add_xml('devices', xml)

    def destroy(self):
        pool = self.other_attribute("pool").used_pool()
        volume = self.get_volume(pool.name(),
                                 self.component_entity(),
                                 raise_exception=False)

        if volume:
            self._remove_volume(volume)

    def _image_store_path(self):
        home = self.io().user_home()
        return paths.xii_home(home, 'images')

    def _image_path(self):
        name = util.md5digest(self.settings())
        self.parent().add_meta("image", name)
        return os.path.join(self._image_store_path(), name)

    def _remove_volume(self, volume):
        volume.wipe(0)
        volume.delete(0)

    def _fetch_image(self):
        _pending.acquire()
        if self.io().exists(self._image_path()):
            _pending.release()
            return

        if self.settings().startswith("http"):
            self.say("downloading image...")
            self.io().download_url(self.settings(), self._image_path())
        else:
            self.say("copy image...")
            self.io().copy(self.settings(), self._image_path())

        (md5, sha256) = self._generate_hashes()

        stats = {
                "source": self.settings(),
                "type": os.path.splitext(self.settings())[1][1:],
                "size": self.io().stat(self._image_path()).st_size,
                "md5": md5,
                "sha256": sha256,
                "added": time.time()
                }

        util.yaml_write(self._image_path() + ".yml", stats)
        _pending.release()

    def _generate_hashes(self):
        try:
            self.say("generate image checksum...")
            md5_hash    = hashlib.md5()
            sha256_hash = hashlib.sha256()
            with open(self._image_path(), 'rb') as hdl:
                buf = hdl.read(65536)
                while len(buf) > 0:
                    md5_hash.update(buf)
                    sha256_hash.update(buf)
                    buf = hdl.read(65536)
            return (md5_hash.hexdigest(), sha256_hash.hexdigest())
        except IOError as err:
            raise error.ExecError("Could not create validation hashes")
