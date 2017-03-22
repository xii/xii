#!/usr/bin/python2

import xml.etree.ElementTree as etree
import libvirt
import socket
import subprocess
import sys
import os

""" xii's forwarding script
TODO
"""

# def fetch_host_ip():
#     # snippet from stackoverflow 166506
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.connect(("8.8.8.8", 0))
#     return sock.getsockname()[0]

    # /sbin/iptables -I FORWARD -o virbr0 -d  $GUEST_IP -j ACCEPT
	# /sbin/iptables -t nat -I PREROUTING -p tcp --dport $HOST_PORT -j DNAT --to $GUEST_IP:$GUEST_PORT


    #     iptables(["-t", "nat", "-A", dnat_chain, "-p", protocol,
    #               "-d", public_ip, "--dport", str(public_port),
    #               "-j", "DNAT", "--to", dest])

    #     iptables(["-t", "nat", "-A", snat_chain, "-p", protocol,
    #               "-s", private_ip, "-d", private_ip, "--dport", str(public_port), "-j", "MASQUERADE"])

    #     iptables(["-t", "filter", "-A", fwd_chain, "-p", protocol,
    #               "-d", private_ip, "--dport", str(private_port), "-j", "ACCEPT"] + interface)




    #     iptables(["-t", "nat", "-A", "OUTPUT", "-p", proto,
    #               "-d", pub, "--dport", pub_p, "-j", "DNAT", "--to", dest])

    #     iptables(["-t", "nat", "-A", "POSTROUTING", "-p", proto,
    #               "-s", priv, "-d", priv, "--dport",
    #               pub_p, "-j", "MASQUERADE"])

    #     iptables(["-t", "filter", "-A", "FORWARD", "-p", proto,
    #               "-d", priv, "--dport", priv_p, "-j", "ACCEPT"])
# <xii:forwards>
#   <xii:port-forward src="80" dest="8088"></xii:port-forward>
# </xii:forwards>

# <xii:node xmlns:xii="http://xii-project.org/xmlns/node/1.0">
#   <xii:definition>/files/dev/xii/examples/port-forward/port-forward.xii</xii:definition>
#   <xii:image>6d454c441f13163d6b395b6af5bbd3e0</xii:image>
#   <xii:user>felixsch</xii:user>
#   <xii:created>1490092697.18</xii:created>
# <xii:forwards>
#   <xii:port-forward src="80" dest="8088"></xii:port-forward>
# </xii:forwards>
# </xii:node>

IPTABLES_BIN = subprocess.check_output(["which", "iptables"]).strip()


def iptables(args):
    print("iptables {}".format(" ".join(args)))
    subprocess.call([IPTABLES_BIN] + args)


def default(key, struct, default=None):
    if key not in struct:
        return default
    return struct[key]


def sysctl_set(path, value):
    print("{} -> {}".format(path, value))
    if (os.path.isfile(path)):
        with open(path, 'w') as brnf:
            brnf.write('{}\n'.format(value))


def set_rule(name, conn, inst, meta, action):
    # add forwardings to chains
    for forward in meta:
        guest_ip = inst[1]
        guest_port = forward["guest-port"]
        host_port = forward["host-port"]
        proto = default("proto", forward, "tcp")
        dest = "{}:{}".format(guest_ip, guest_port)
        interface = ["-o", forward["interface"]] if "interface" in forward else []
        host_ip = ["-d", forward["host-ip"]] if "host-ip" in forward else []

        # iptables(["-t", "nat", action, "OUTPUT", "-p", "tcp", "-o", "lo",
        #           "--dport", host_port, "-j", "REDIRECT", "--to-ports", guest_port])

        iptables(["-t", "nat", action, "OUTPUT", "-p", proto] + host_ip +
                  ["--dport", host_port, "-j", "DNAT", "--to", dest])

        iptables(["-t", "nat", action, "POSTROUTING", "-p", proto,
                  "-s", guest_ip, "-d", guest_ip, "--dport",
                  host_port, "-j", "MASQUERADE"])

        iptables(["-t", "filter", action, "FORWARD", "-p", proto,
                  "-d", guest_ip, "--dport", guest_port, "-j", "ACCEPT"])

        # iptables([action, "FORWARD", "-d", guest_ip, "-m", "state", "--state",
        #           "NEW,ESTABLISHED,RELATED", "-j", "ACCEPT"] + interface)

        # iptables(["-t", "nat", action, "PREROUTING", "-p", proto,] + host_ip +
        #          ["--dport", host_port, "-j", "DNAT", "--to", dest])


def enable_forwarding(name, conn, inst, meta):
    sysctl_set("/proc/sys/net/bridge/bridge-nf-call-iptables", 0)
    sysctl_set("/proc/sys/net/ipv4/ip_forward", 1)
    set_rule(name, conn, inst, meta, "-A")


def disable_forwarding(name, conn, inst, meta):
    set_rule(name, conn, inst, meta, "-D")


def parse_meta(inst):
    ns = { "xii": "http://xii-project.org/xmlns/node/1.0" }
    root = etree.fromstring(inst[0].XMLDesc())
    meta = root.find("metadata")

    if meta is None:
        return None

    return map(lambda x: x.attrib, meta.findall("xii:node/forwards/port", ns))

def connect_libvirt(url="qemu:///system"):
    try:
        return libvirt.open(url)
    except libvirt.libvirtError as e:
        raise RuntimeError("libvirt connection failed: {}".format(e))


def fetch_domain(conn, name):
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
