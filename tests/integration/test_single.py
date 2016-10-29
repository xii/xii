import pytest


from integration import runner, file


def test_single_domain():
    env_vars = runner.load_variables_from_env()
    single   = file.get_test_path("single")

    for a in ["start", "suspend", "resume", "stop", "destroy"]:
        runner.run_xii(deffile=single, variables=env_vars, cmd=a)
