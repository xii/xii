from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as etree

import libvirt

from xii import error
from xii.output import warn


class Connection():
    __metaclass__ = ABCMeta

    def __init__(self, uri, dfn, conf):
        self.dfn = dfn
        self.conf = conf
        self.libvirt = None
        self.uri = uri

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

    def get_capabilities(self, arch='x86_64', prefare_kvm=True):
        try:
            caps = etree.fromstring(self.virt().getCapabilities())
            cpu_arch = caps.find('host/cpu/arch').text
            cpu_model = caps.find('host/cpu/model').text
            guests = {}

            for guest in caps.findall('guest'):
                guest_arch = guest.find('arch').attrib['name']
                emu_type = 'qemu'
                emu  = guest.find('arch/emulator').text
                host = guest.find('arch/machine[@canonical]').attrib['canonical']

                # prefare kvm if possible
                kvm = guest.find("arch/domain[@type='kvm']")
                if kvm is not None:
                    emu_type = 'kvm'
                    emu = kvm.find('emulator')
                    host = kvm.find('machine[@canonical]').attrib['canonical']

                guests[guest_arch] = {'emulator_type': emu_type,
                                'emulator': emu.text,
                                'host': host}
            return {'arch': arch,
                    'model': cpu_model,
                    'emulator': guests[arch]['emulator'],
                    'emulator_type': guests[arch]['emulator_type'],
                    'host': guests[arch]['host']}
        except libvirt.libvirtError as err:
            raise error.LibvirtError(err)
            
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
    def download(self, msg, source, dest):
        pass

    @abstractmethod
    def chmod(self, path, new_mode, append=False):
        pass




def establish(dfn, conf):
    from xii.connections.local import Local
    uri = dfn.settings('connection', conf.default_host())

    # if uri.startswith('qemu+ssh'):
    #     return Remote(uri, dfn, conf)
    if uri.startswith('qemu'):
        return Local(uri, dfn, conf)

    raise RuntimeError("Unsupported connection. Currently onlye qemu:// "
                       "and qemu+ssh:// is supported")
