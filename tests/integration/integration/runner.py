import os
import subprocess

import pytest

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
    print("calling `{}`".format(" ".join(call)))

    process = subprocess.Popen(call, stdout=subprocess.PIPE, env=xii_env)

    for line in process.stdout:
        print("> " + line.rstrip(os.linesep))

    process.communicate()


    if process.returncode != returncode:
        pytest.fail("Excepted xii to return {} but it returned {}"
                     .format(returncode, process.returncode))

    return True


def cleanup_instance(instance, pool="default", connection="qemu:///system"):
    def _run(args):
        print(" ".join(args))
        subprocess.call(args)

    print("[cleanup] ---------------------------------------------------------")
    _run(["virsh", "-c", connection, "destroy", instance])
    _run(["virsh", "-c", connection, "undefine", instance])
    _run(["virsh", "-c", connection, "vol-delete", instance, pool])
    print("-------------------------------------------------------------------")







