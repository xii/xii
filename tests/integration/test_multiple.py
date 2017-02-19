import pytest

from integration import runner, file, ssh

hosts = ["multiple-1", "multiple-2"]

@runner.cleanup_node(hosts, "qemu:///system")
def test_multi_nodes():
    """ 
    run 3 instances at the same time. Make sure ssh works correctly
    and hostname is set to instance name
    """

    env_vars = runner.load_variables_from_env()
    multiple   = file.get_test_path("multiple")
 
    runner.run_xii(deffile=multiple, variables=env_vars, cmd="start")

    for host in hosts:
        con = ssh.connect_to(host, "root", "linux", multiple)
        assert(con.run("hostname") == host)

    runner.run_xii(deffile=multiple, variables=env_vars, cmd="destroy")
