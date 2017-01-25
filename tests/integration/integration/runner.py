import os
import subprocess
import libvirt
import pytest

import xml.etree.ElementTree as etree


def libvirt_connect(url):
        def _error_handler(_, err):
            pytest.fail("!!! {}".format(err[2]), pytrace=False)

        libvirt.registerErrorHandler(_error_handler, ctx=None)
        virt = libvirt.open(url)

        if not virt:
            pytest.fail("Could not establish libvirt connection")
        return virt


def libvirt_resource(virt, resource, name, volname=None):
    mapping = {
        "domain": "lookupByName",
        "pool": "storagePoolLookupByName",
        "network": "networkLookupByName",
    }
    try:
        if resource == "volume":
            pool = libvirt_resource(virt, "pool", name)
            if not pool:
                return None
            return pool.storageVolLookupByName(volname)
        return getattr(virt, mapping[resource])(name)
    except libvirt.libvirtError:
        return None


def cleanup_node(nodes, url):
    if not isinstance(nodes, list):
        nodes = [nodes]

    def cleanup_wrap(func):
        def func_wrapper(*args):
            try:
                func(*args)
            finally:
                virt = libvirt_connect(url)
                for name in nodes:
                    node = libvirt_resource(virt, "domain", name)
                    if node is None:
                        continue

                    xml = etree.fromstring(node.XMLDesc())
                    for source in xml.findall("devices/disk/source"):
                        pool = source.attrib["pool"]
                        vol_name = source.attrib["volume"]

                        volume = libvirt_resource(virt, "volume", pool, vol_name)
                        if volume is None:
                            continue
                        print("[cleanup] remove vol {}".format(volume.name()))
                        volume.wipe(0)
                        volume.delete(0)
                    print("[cleanup] remove node {}".format(node.name()))
                    node.destroy()
                    node.undefine()
        return func_wrapper
    return cleanup_wrap


def load_variables_from_env(prefix="XII_"):
    length = len(prefix)
    vars   = {}

    for var in filter(lambda x: x.startswith(prefix), os.environ):
        vars[var[length:]] = os.environ[var]
    return vars


def run_xii(deffile, cmd, variables={}, gargs=None, cargs=None, returncode=0):

    xii_env = os.environ.copy()

    for key, value in variables.items():
        print("=> XII_" + key + " defined")
        xii_env["XII_" + key] = value

    call = ["xii", "--no-parallel", "--deffile", deffile, cmd]
    print("[call]: {}".format(" ".join(call)))

    process = subprocess.Popen(call,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE,
                               shell=False)


    for output in iter(process.stdout.readline, ""):
        print("> " + output.decode('utf-8').strip())

    process.communicate()

    if process.returncode != returncode:
        pytest.fail("Excepted xii to return {} but it returned {}"
                     .format(returncode, process.returncode),
                     pytrace=False)

    return True
