import pytest


from integration import runner, file


@runner.cleanup_node("single", "qemu:///system")
def test_single_domain():
    env_vars = runner.load_variables_from_env()
    single   = file.get_test_path("single")
 
    runner.run_xii(deffile=single, variables=env_vars, cmd="start")
    #runner.run_xii(deffile=single, variables=env_vars, cmd="destroy")
