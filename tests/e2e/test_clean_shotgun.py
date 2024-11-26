from src.autobfx.scripts.run import main as Run


def test_clean_shotgun(dummy_project, test_runner):
    # Consider a way to modify config file to use test runner, dry runner is fine for now

    flow_run = Run([str(dummy_project.project_fp), "clean_shotgun:clean_shotgun_flow"])

    print(flow_run)
    print(flow_run.name)
    print(flow_run.flow_id)
    print(flow_run.state_id)
    print(flow_run.tags)

    assert False
