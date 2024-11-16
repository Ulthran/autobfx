import argparse
import os
from autobfx.lib.config import Config
from importlib.machinery import SourceFileLoader
from prefect.deployments import run_deployment
from pathlib import Path


def main(argv):
    parser = argparse.ArgumentParser(description="Run a flow")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    parser.add_argument("flow", type=str, help="The flow to run")
    args = parser.parse_args(argv)

    project_fp = Path(args.project_fp).absolute()
    flow_id = args.flow

    os.makedirs(project_fp, exist_ok=True)
    os.makedirs(project_fp / ".autobfx" / "done", exist_ok=True)

    config_source = SourceFileLoader(
        "config", str(Path(args.project_fp).absolute() / "config.py")
    ).load_module()
    config = Config(**config_source.config)

    from autobfx.flows import flows
    from autobfx.flows import root as main_root

    # TODO Once we have plugins they should be imported here (somehow find all 'autobfx-...' packages and import __dict__)
    # Is this also the place to update the runner_map if it needs it?

    try:
        flow = flows[flow_id]
    except KeyError:
        raise KeyError(f"Flow '{flow_id}' not found in: {flows.keys()}")

    flow.from_source(
        source=str(main_root),
        entrypoint=f"{flow_id.split(':')[0]}.py:{flow_id.split(':')[1]}",
    ).deploy(
        name=f"{flow_id}_deployment",
        work_pool_name="default",
        ignore_warnings=True,
    )

    run_deployment(
        f"{flow_id.split(':')[0]}/{flow_id}_deployment",
        parameters={
            "config": config.dict(),
        },
    )
