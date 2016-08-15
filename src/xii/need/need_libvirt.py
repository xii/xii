import libvirt
import xml.etree.ElementTree as etree

from abc import ABCMeta, abstractmethod

from xii import error


class NeedLibvirt():

    @abstractmethod
    def get_virt_url(self):
        pass

    def virt(self):
        def _error_handler(_, err):
            if err[3] != libvirt.VIR_ERR_ERROR:
                warn("Non-error from libvirt: '{}'".format(err[2]))
            else:
                raise error.ConnError("[libvirt] {}".format(err[2]))

        def _create_connection():
            libvirt.registerErrorHandler(_error_handler, ctx=None)

            url = self.get_virt_url()

            if not url:
                raise error.ConnError("[libvirt] No connection url supplied")

            virt = libvirt.open(url)

            if not virt:
                raise error.ConnError("[libvirt] Could not connect "
                                      "to {}".format(url))
            return virt
        return self.share("libvirt", _create_connection)


    def get_domain(self, name, raise_exception=True):
        try:
            return self.virt().lookupByName(name)
        except libvirt.libvirtError:
            if raise_exception:
                raise error.NotFound("Could not find domain "
                                        "({})".format(name))
            else:
                return None

    def get_pool(self, name, raise_exception=True):
        try:
            return self.virt().storagePoolLookupByName(name)
        except libvirt.libvirtError:
            if raise_exception:
                raise error.NotFound("Could not find pool "
                                     "({})".format(name))
            else:
                return None

    def get_network(self, name, raise_exception=True):
        try:
            return self.virt().networkLookupByName(name)
        except libvirt.libvirtError:
            if raise_exception:
                raise error.NotFound("Could not find network "
                                     "({})".format(name))
            else:
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
