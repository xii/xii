import pytest


from integration import runner, file, ssh


@runner.cleanup_node("single", "qemu:///system")
def test_single_domain():
    """
    Test simple one instance run and if password user creation works
    """

    env_vars = runner.load_variables_from_env()
    single   = file.get_test_path("single")
 
    runner.run_xii(deffile=single, variables=env_vars, cmd="start")
    con = ssh.connect_to("single", "root", "linux", single)
    assert(con.stat("/etc/shadow"))
    runner.run_xii(deffile=single, variables=env_vars, cmd="destroy")
