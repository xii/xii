#!/usr/bin/python2
from __future__ import print_function

import xml.etree.ElementTree as etree
import subprocess
import sys
import re
import os
import time
import json

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
STATUS_PATH = "/var/lib/libvirt/dnsmasq/{}.status"
CONF_PATH = "/var/lib/libvirt/dnsmasq/{}.conf"

# set this to true if you want to debug the script
# this will create the file /tmp/xii-hook-debug
DEBUG = True


def debug(msg):
    """record debug messages

    Args:
        msg     message which should be send to debug file

    Returns:
        nothing
    """
    if not DEBUG:
        return
    if debug._hdl is None:
        debug._hdl = open("/tmp/xii-hook-debug-{}".format(debug._name), "w+")

    print("[{}] {}".format(name, msg), file=debug._hdl)
# initialize static var
debug._hdl = None


def read_file(path):
    """read a file and return its content

    Args:
        path    path to the file which should be read

    Returns:
        the content of the file as string

    Throws:
        RuntimerError if an error has occured
    """
    try:
        with open(path, 'r') as stream:
            return stream.read()
    except IOError:
        raise RuntimeError("Could not read file {}!".format(path))


def iptables(args):
    """ run iptables with additional arguments

    Args:
        args    iptables arguments as list

    Returns:
        nothing
    """
    debug(" ".join([IPTABLES_BIN] + args))
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
    set_rule(ip, meta, "-D")


def fetch_guest_ip(xml):
    """fetch guest ip address without using any libvirt methods

    This script needs to find out the used network and fetch the
    interface name to check the dnsmasq status file to fetch dhcp
    leases for the domain. Matched is via the obtained mac address.

    Note:
        this script waits until dnsmasq has assigned a ip address to
        the host.

    Args:
        xml     already parsed xml object

    Returns:
        the ipv4 address of the domain

    Throws:
        throws either a JSON Decode error or RuntimeError
    """
    # parse domain xml to get network name and instance mac address
    interface = xml.find("devices/interface[@type='network']")
    network = interface.find("source").attrib["network"]
    mac = interface.find("mac").attrib["address"]

    debug("interface = {}".format(interface))
    debug("network = {}".format(network))
    debug("mac = {}".format(mac))

    # load the network configuration and fetch the used interface
    # to check dhcp leases
    for i in range(0, 10):
        if os.path.exists(CONF_PATH.format(network)):
            break
        debug("#{} waiting for configuration...".format(i))
        time.sleep(2)

    # parse the interface name
    conf = read_file(CONF_PATH.format(network))
    matched = re.search("interface=(\w+\d{1,})", conf)

    if not matched:
        raise RuntimeError("Could not find used interface")

    iface = matched.group(1)
    debug("iface = {}".format(iface))

    # wait for the status file which includes all dhcp leases
    # from dnsmasq. Fetch the required ip address from there
    for i in range(0, 100):
        debug("#{} waiting for iface file status...".format(i))
        status = read_file(STATUS_PATH.format(iface))

        # status file does not include a [] or {} when empty so
        # it is not a valid json file.
        if len(status) != 0:
            status = json.loads(status)
            mapping = filter(lambda s: s["mac-address"] == mac, status)
            if len(mapping) == 1:
                return mapping[0]["ip-address"]
        time.sleep(2)

    raise RuntimeError("Could not fetch ip address. If this error "
                       "still persists, please report this error at "
                       "https://github.com/xii/xii/issues")


def fetch_port_forwards(xml):
    """fetch defined port forwards from node meta

    Args:
        xml    xml data as etree object

    Returns:
        a list of all portforwards (as dict)
    """
    ns = {"xii": "http://xii-project.org/xmlns/node/1.0"}
    meta = xml.find("metadata")

    if meta is None:
        debug("No metadata found, skipping...")
        return []

    return map(lambda x: x.attrib, meta.findall("xii:node/forwards/port", ns))


def parse_xml():
    """ parse xii meta data from a domain

    It fetches the metadata from the xml description of
    a domain.

    Args:
        inst    domain instance object

    Returns:
        the portforwardings as list of dicts
    """

    # Read xml description from stdin
    # check https://www.libvirt.org/hooks.html#arguments
    xml = sys.stdin.read()
    debug(xml)
    root = etree.fromstring(xml)

    if root is None:
        return None
    return root


# Run this actions on different qemu states
ACTION_TABLE = {
    "started": [enable_forwarding],
    "stopped": [disable_forwarding],
    "reconnect": [disable_forwarding, enable_forwarding]
}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Invalid arguments: {}".format(sys.argv), file=sys.stderr)
        sys.exit(1)

    name, action = sys.argv[1:3]

    debug._name = name
    debug("start[{}/{}]".format(name, action))
    try:
        # check if action is defined
        if action not in ACTION_TABLE:
            sys.exit(0)

        xml = parse_xml()
        fwd = fetch_port_forwards(xml)

        # no valid xii created domain found
        # or no port forwards
        if not fwd:
            debug("no forwards defined!")
            sys.exit(0)
        ip = fetch_guest_ip(xml)

        map(lambda f: f(ip, fwd), ACTION_TABLE[action])
        debug("done [{}]".format(name))
    except RuntimeError as e:
        print("FAILED: {}".format(e), file=sys.stderr)
        debug("FAILED: {}".format(e))
        sys.exit(1)
