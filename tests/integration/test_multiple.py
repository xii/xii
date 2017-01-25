import pytest


from integration import runner, file


@runner.cleanup_node(["multiple-1", "multiple-2", "multiple-3"], "qemu:///system")
def test_multi_nodes():
    env_vars = runner.load_variables_from_env()
    multiple   = file.get_test_path("multiple")
 
    runner.run_xii(deffile=multiple, variables=env_vars, cmd="start")
    runner.run_xii(deffile=multiple, variables=env_vars, cmd="destroy")
