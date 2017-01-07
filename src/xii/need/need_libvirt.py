import libvirt
import xml.etree.ElementTree as etree

from time import sleep
from abc import ABCMeta, abstractmethod

from xii import error
from xii.output import HasOutput


class NeedLibvirt(HasOutput):

    @abstractmethod
    def get_virt_url(self):
        pass

    def virt(self):
        """ get the libvirt handle

        Connects to a libvirt host using the standard uri scheme

        Returns:
            A libvirt handle connected to the libvit host
        """
        def _error_handler(_, err):
            if err[3] != libvirt.VIR_ERR_ERROR:
                self.warn("Non-error from libvirt: '{}'".format(err[2]))
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

        def _close_connection(virt):
            virt.close()


        return self.share("libvirt", _create_connection, _close_connection)

    def get_resource(self, typ, *args, **kwargs):
        """returns a libvirt resource

        search a libvirt resource. `typ` defines which type should be searched.
        Currently supported is:

        * domain
        * pool
        * network
        * volume

        Args:
            typ: Resource type
            args: name or the resource or in case of volume name of the pool and
                  name of the volume
            kwargs: either throw or raise_exception set to boolean

        Returns:
            Returns the searched resource or None if set non throwing

        Throws:
            If throw or raise_exception is not set to False a exception is
            raised if the resource could not be found
        """
        r = True
        if "raise_exception" in kwargs:
            r = kwargs["raise_exception"]
        if "throw" in kwargs:
            r = kwargs["throw"]

        mapping = {
            "domain": "lookupByName",
            "pool": "storagePoolLookupByName",
            "network": "networkLookupByName",
        }

        try:
            if typ == "volume":
                pool = self.get_resource("pool", args[0], throw=r)
                if not pool:
                    return None
                return pool.storageVolLookupByName(args[1])

            return getattr(self.virt(), mapping[typ])(*args)
        except libvirt.libvirtError:
            if r:
                raise error.NotFound("Could not find {}"
                                     "({})".format(typ, name))
            return None


    def get_network(self, name, raise_exception=True):
        """Get a network resource

        Args:
            name: Name of the resource
            raise_exception: Should this method raise a exception if no resource
                             is found

        Returns:
            Network object or None if not found

        Throws:
            A exception if not disabled via raise_exception
        """
        r = raise_exception
        return self.get_resource("network", name, throw=r)

    def get_volume(self, pool_name, name, raise_exception=True):
        """Get a volume resource

        Args:
            pool_name: Name of the pool
            name: Name of the volume
            raise_exception: Should this method raise a exception if no resource
                             is found

        Returns:
            Volume object or None if not found

        Throws:
            A exception if not disabled via raise_exception
        """
        r = raise_exception
        return self.get_resource("volume", pool_name, name, throw=r)

    def get_domain(self, name, raise_exception=True):
        """Get a domain resource

        Args:
            name: Name of the domain
            raise_exception: Should this method raise a exception if no resource
                             is found

        Returns:
            Domain object or None if not found

        Throws:
            A exception if not disabled via raise_exception
        """
        r = raise_exception
        return self.get_resource("domain", name, throw=r)

    def get_pool(self, name, raise_exception=True):
        """get a pool resource

        Args:
            name: Name of the pool
            raise_exception: Should this method raise a exception if no resource
                             is found

        Returns:
            Pool object or None if not found

        Throws:
            A exception if not disabled via raise_exception
        """
        r = raise_exception
        return self.get_resource("pool", name, throw=r)

    def wait_for_resource(self, *args):
        """block until a resource exists

        Call _`get_resource` until a the resource exists.

        Args:
            See _`get_resource`

        Returns:
            The requested resource

        Throws:
            See _`get_resource`
        """
        resource = self.get_resource(*args, raise_exception=False)
        if resource:
            return resource

        for _ in range(self.global_get("global/retry", 20)):
            resource = self.get_resource(*args, raise_exception=False)

            if resource:
                return resource
            sleep(self.global_get("global/wait", 3))
        return None

    def get_capabilities(self, arch='x86_64', prefer_kvm=True):
        """get libvirt capabilities
        """
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


    def domain_get_ip(self, domain_name, retry=20, wait=3):
        """fetch ipv4 for a given domain name

        Args:
            domain_name: Domain name
            retry: n times until exception
            wait: n seconds between each cycle

        Returns:
            Returns the bound ipv4 address
        """

        domain = self.get_domain(domain_name)
        nets = []

        if not domain.isActive():
            return False

        for i in range(retry):

            self.counted(i, "fetching ip address from {}...".format(domain_name))
            nets = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)

            if len(nets):
                break
            sleep(wait)

        if not len(nets):
            raise error.ConnError("Could not fetch ip address for {}. Giving up!"
                                  .format(domain_name))

        net = nets.itervalues().next()

        if not len(net['addrs']):
            return False

        return net['addrs'][0]['addr']

    def network_get_host_ip(self, network_name, version="ipv4"):
        """get host ip for a virtual network

        Args:
            network_name: Name of the virtual network
            version: ipv4 or ipv6

        Returns:
            A ipv4 or ipv6 address
        """
        network = self.get_network(network_name, raise_exception=False)

        if not network:
            return None

        xml = etree.fromstring(network.XMLDesc())
        ips = xml.findall("ip")

        for ip in ips:
            if "family" in ip.attrib:
                if ip.attrib["family"] == version:
                    return ip.attrib["address"]
            else:
                if version == "ipv4":
                    return ip.attrib["address"]

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
