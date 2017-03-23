#!/usr/bin/python2

import xml.etree.ElementTree as etree
import libvirt
import subprocess
import sys
import os

""" xii's port forwarding script
simple port forwading script which is used as hook for the libvirt qemu
implementation.

Args:
    name    name of the domain which is handled
    action  action which should be executred (start/stopped/restarted)

Returns:
    returns 0 on succcess and 1 on error
"""

# def fetch_host_ip():
#     """ a easy way to get used external ip
#
#     Returns:
#         nothing
#     """
#     # snippet from stackoverflow 166506
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.connect(("8.8.8.8", 0))
#     return sock.getsockname()[0]

IPTABLES_BIN = subprocess.check_output(["which", "iptables"]).strip()


def iptables(args):
    """ run iptables with additional arguments

    Args:
        args    iptables arguments as list

    Returns:
        nothing
    """
    subprocess.call([IPTABLES_BIN] + args)


def sysctl_set(path, value):
    """set values in /proc path

    Args:
        path    path which should be altered
        value   value which should be written

    Returns:
        Nothing
    """
    if (os.path.isfile(path)):
        with open(path, 'w') as brnf:
            brnf.write('{}\n'.format(value))


def set_rule(ip, meta, action):
    """set iptables rules for forwarding a port to a virtual maschine

    Args:
        ip      ipv4 address of the domain
        meta    portforwarding metadata of the domain
        action  iptables action ("-I" or "-A" or "-D")

    Returns:
        nothing
    """
    for forward in meta:
        guest_ip = ip
        guest_port = forward["guest-port"]
        host_port = forward["host-port"]
        proto = forward["proto"] if "proto" in forward else "tcp"

        dest = "{}:{}".format(guest_ip, guest_port)

        iptables(["-t", "nat", action, "OUTPUT", "-p", "tcp", "--dport",
                  host_port, "-j", "DNAT", "--to-destination", dest])

        iptables(["-t", "nat", action, "POSTROUTING", "-p", proto, "-d",
                  guest_ip, "--dport", guest_port, "-j", "MASQUERADE"])


def enable_forwarding(ip, meta):
    """enable port forwarding for one domain and set
       required sysctl flags

    Args:
        ip      ipv4 address of the domain
        meta    portforwarding metadata of the domain

    Returns:
        nothing
    """
    sysctl_set("/proc/sys/net/bridge/bridge-nf-call-iptables", 0)
    sysctl_set("/proc/sys/net/ipv4/ip_forward", 1)
    sysctl_set("/proc/sys/net/ipv4/conf/all/route_localnet", 1)
    set_rule(ip, meta, "-A")


def disable_forwarding(ip, meta):
    """disable port forwarding for one domain

    Args:
        ip      ipv4 address of the domain
        meta    portforwarding metadata of the domain

    Returns:
        nothing
    """
    set_rule(name, conn, inst, meta, "-D")


def parse_meta(inst):
    """ parse xii meta data from a domain

    It fetches the metadata from the xml description of
    a domain.

    Args:
        inst    domain instance object

    Returns:
        the portforwardings as list of dicts
    """
    ns = {"xii": "http://xii-project.org/xmlns/node/1.0"}
    root = etree.fromstring(inst[0].XMLDesc())
    meta = root.find("metadata")

    if meta is None:
        return None

    return map(lambda x: x.attrib, meta.findall("xii:node/forwards/port", ns))


def connect_libvirt(url="qemu:///system"):
    """connect to libvirt system

    Args:
        url     the connection url to the _qemu_ system

    Returns:
        the libvirt connection object
    """
    try:
        return libvirt.open(url)
    except libvirt.libvirtError as e:
        raise RuntimeError("libvirt connection failed: {}".format(e))


def fetch_domain(conn, name):
    """fetch domain data from libvirt connection

    Args:
        conn    libvirt connection object
        name    name of the domain/node/instance

    Returns:
        a tuple with (libvirt domain object, ip4v address of the domain)
    """
    try:
        domain = conn.lookupByName(name)
        nets = domain.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE
        )

        if not len(nets):
            raise RuntimeError("Could not fetch ipv4 address for {}"
                               .format(name))

        net = nets.itervalues().next()

        return (domain, net["addrs"][0]['addr'])
    except libvirt.libvirtError as e:
        raise RuntimeError("could not find domain {}.".format(e))

# Run this actions on different qemu states
ACTION_TABLE = {
    "start": [enable_forwarding],
    "stopped": [disable_forwarding],
    "reconnect": [disable_forwarding, enable_forwarding]
}


if __name__ == "__main__":
    name, action = sys.argv[1:3]
    try:
        conn = connect_libvirt()
        inst = fetch_domain(conn, name)
        meta = parse_meta(inst)

        if meta is None:
            sys.exit(0)

        map(lambda f: f(name, conn, inst, meta), ACTION_TABLE[action])
    except RuntimeError as e:
        print("FAILED: {}".format(e))
        sys.exit(1)
