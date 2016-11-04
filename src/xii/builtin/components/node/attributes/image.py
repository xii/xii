import os
import time

from multiprocessing import Condition

from xii import paths, error, entity, need, util

from xii.attribute import Attribute
from xii.validator import String
from xii.entity import EntityRegister

_pending = Condition()

class ImageAttribute(Attribute, need.NeedIO, need.NeedLibvirt):
    atype = "image"

    requires = ['pool']
    keys = String()

    def __init__(self, component):
        Attribute.__init__(self, component)
        self._tempdir = self.io().mktempdir("xii-" + self.component_entity())

    def get_tmp_volume_path(self):
        return os.path.join(self._tempdir, "image")

    def spawn(self):
        # create image store if needed
        if not self.io().exists(self._image_store_path()):
            self.io().mkdir(self._image_store_path(), recursive=True)

        pool_name = self.other_attribute("pool").used_pool_name()
        pool_type = self.other_attribute("pool").used_pool_type()

        volume = self.get_volume(pool_name, self.component_entity(), raise_exception=False)

        if volume:
            self._remove_volume(volume)

        if not self.io().exists(self._image_path()):
            self._fetch_image()

        self.say("cloning image...")
        self.io().copy(self._image_path(), self.get_tmp_volume_path())

    def after_spawn(self):
        pool = self.other_attribute("pool").used_pool()
        size = self.io().stat(self.get_tmp_volume_path()).st_size
        volume_tpl = paths.template("volume.xml")
        xml = volume_tpl.safe_substitute({
            "name": self.component_entity(),
            "capacity": size
            })

        # FIXME: Add error handling
        volume = pool.createXML(xml)

        def read_handler(stream, data, file_):
            return file_.read(data)

        self.say("importing...")
        with open(self.get_tmp_volume_path(), 'r') as image:
            stream = self.virt().newStream(0)
            volume.upload(stream, 0, 0, 0)
            stream.sendAll(read_handler, image)
            stream.finish()

        disk_tpl = paths.template("disk.xml")
        xml = disk_tpl.safe_substitute({
            "pool": pool.name(),
            "volume": self.component_entity()
        })

        self.parent().add_xml('devices', xml)
        self.io().rm(self._tempdir)

    def destroy(self):
        pool = self.other_attribute("pool").used_pool()
        volume = self.get_volume(pool.name(), self.component_entity(), raise_exception=False)

        if volume:
            self._remove_volume(volume, force=True)

    def _image_store_path(self):
        home = self.io().user_home()
        return paths.xii_home(home, 'images')

    def _image_path(self):
        return os.path.join(self._image_store_path(), util.md5digest(self.settings()))

    def _remove_volume(self, volume, force=False):
        if self.g_get('global/auto_delete_volumes', False) or force:
            return volume.delete()
        raise error.ExecError(
                ["Volume `{}` already exists".format(self.component_entity()),
                    "If you want xii to automatically delete volumes",
                    "set auto_delete_volumes to True in your xii configuration"])

    def _fetch_image(self):
        _pending.acquire()
        if self.io().exists(self._image_path()):
            _pending.release()
            return

        if self.settings().startswith("http"):
            self.say("downloading image...")
            self.io().download(self.settings(), self._image_path())
        else:
            self.say("copy image...")
            self.io().copy(self.settings(), self._image_path())

        _pending.release()


EntityRegister.register_attribute("node", ImageAttribute)
