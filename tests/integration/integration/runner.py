import os
import subprocess

def load_variables_from_env(prefix="XII_INTEGRATION_"):
    length = len(prefix)
    vars   = {}

    for var in filter(lambda x: x.startswith(prefix), os.environ):
        vars[var[length:]] = os.environ[var]
    return vars


def run_xii(deffile, cmd, variables={}, gargs=None, cargs=None):

    xii_env = os.environ.copy()
    
    for key, value in variables.items():
        print("=> XII_" + key + " defined")
        xii_env["XII_" + key] = value

    call = ["xii", "--no-parallel", "--deffile", deffile, gargs, cmd, cargs]
    print("calling `{}`".format(" ".join(filter(None, call))))
 
    process = subprocess.Popen(call, stdout=subprocess.PIPE, env=xii_env)

    for line in process.stdout:
        print("> " + line.rstrip(os.linesep))

    if process.returncode != 0:
        raise RuntimeError("running xii failed")


    

    
 


