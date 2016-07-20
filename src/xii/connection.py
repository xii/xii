from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as etree

import libvirt
import guestfs

import os

from xii import error
from xii.output import warn


class Connection():
    __metaclass__ = ABCMeta

    def __init__(self, uri, dfn, conf):
        self.dfn = dfn
        self.conf = conf
        self.libvirt = None
        self.uri = uri
        self.guests = {}

    def virt(self):
        def error_handler(_, err):
            if err[3] != libvirt.VIR_ERR_ERROR:
                warn("Non-error from libvirt: '{}'".format(err[2]))

        if self.libvirt:
            return self.libvirt

        libvirt.registerErrorHandler(f=error_handler, ctx=None)

        self.libvirt = libvirt.open(self.uri)

        if not self.libvirt:
            raise error.LibvirtError(None, "Could not connection to `{}`".format(self.uri))
        return self.libvirt

    def guest(self, image_path):
        name = os.path.basename(os.path.splitext(image_path)[0])
        if name in self.guests:
            return self.guests[name]

        guest = guestfs.GuestFS()

        if not self.exists(image_path):
            raise error.DoesNotExist("unable to load image. {}: "
                                     "No such file or directory".format(image_path))
        guest.add_drive(image_path)
        guest.launch()
        guest.mount("/dev/sda1", "/")

        self.guests[name] = guest

        return self.guests[name]

    def close_guest(self, image_path):
        if image_path in self.guests:
            guest = self.guests[image_path]

            guest.sync()
            guest.umount("/")
            guest.close()

    def get_domain(self, name):
        try:
            return self.virt().lookupByName(name)
        except libvirt.libvirtError:
            return None

    def get_pool(self, name):
        try:
            return self.virt().storagePoolLookupByName(name)
        except libvirt.libvirtError:
            return None

    def get_network(self, name):
        try:
            return self.virt().networkLookupByName(name)
        except libvirt.libvirtError:
            return None

    def get_capabilities(self, arch='x86_64', prefer_kvm=True):
        try:
            capabilities = self.virt().getCapabilities()
        except libvirt.libvirtError as err:
            raise error.LibvirtError(err)

        emulators = self._parse_capabilities(capabilities, prefer_kvm)

        if arch not in emulators:
            raise error.LibvirtError("Checkout your qemu installation",
                                     "Could not find requiered archtitecture "
                                     "`{}`".format(arch))
        return emulators[arch]

    def _parse_capabilities(self, text, prefer_kvm=True):
        caps = etree.fromstring(text)
        emulators = {}

        # get basic host informations
        cpu = caps.find('host/cpu/model').text
        secmodel = caps.find('host/secmodel/model').text

        # iterate trough emulators

        for emulator in caps.findall('guest'):
            emulator = emulator.find('arch')

            arch = emulator.attrib['name']
            domain_type = emulator.find('domain').attrib['type']

            if prefer_kvm:
                kvm = emulator.find("domain[@type='kvm']")
                if kvm is not None:
                    emulator = kvm
                    domain_type = 'kvm'

            emu = emulator.find('emulator').text

            # check if there is a canonical machine available. If not
            # get the first of the list
            machine = emulator.find('machine[@canonical]')
            if machine is None:
                machine = emulator.find('machine')

            emulators[arch] = {'arch': arch,
                               'cpu': cpu,
                               'secmodel': secmodel,
                               'domain_type': domain_type,
                               'emulator': emu,
                               'machine': machine.text}
        return emulators

    @abstractmethod
    def mkdir(self, directory, recursive=False):
        pass

    @abstractmethod
    def exists(self, path):
        pass

    @abstractmethod
    def user(self):
        pass

    @abstractmethod
    def user_home(self):
        pass

    @abstractmethod
    def copy(self, msg, source, dest):
        pass

    @abstractmethod
    def remove(self, path):
        pass

    @abstractmethod
    def download(self, msg, source, dest):
        pass

    @abstractmethod
    def chmod(self, path, new_mode, append=False):
        pass

    @abstractmethod
    def chown(self, path, uid=None, guid=None):
        pass


def establish(dfn, conf):
    from xii.connections.local import Local
    from xii.connections.ssh import Ssh
    uri = dfn.settings('connection', conf.default_host())

    if uri.startswith('qemu+ssh'):
        return Ssh(uri, dfn, conf)
    if uri.startswith('qemu'):
        return Local(uri, dfn, conf)

    raise RuntimeError("Unsupported connection. Currently onlye qemu:// "
                       "and qemu+ssh:// is supported")
