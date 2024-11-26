import argparse
import os
import time
from autobfx.lib.config import Config, FlowConfig
from autobfx.scripts.server import main as Server
from autobfx.scripts.worker import main as Worker
from httpx import ConnectError
from importlib.machinery import SourceFileLoader
from prefect.client.schemas import FlowRun
from prefect.deployments import run_deployment
from pathlib import Path


def deploy_and_run(
    flow: callable, flow_id: str, work_pool_name: str, config: Config, main_root: Path
):
    flow.from_source(
        source=str(main_root),
        entrypoint=f"{flow_id.split(':')[0]}.py:{flow_id.split(':')[1]}",
    ).deploy(
        name=f"{flow_id}_deployment",
        work_pool_name=work_pool_name,
        ignore_warnings=True,
    )

    return run_deployment(
        f"{flow_id.split(':')[0]}/{flow_id}_deployment",
        parameters={
            "config": config.dict(),
        },
    )


def main(argv) -> FlowRun:
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

    dummy_runner = config.get_runner(FlowConfig())
    work_pool_name = dummy_runner.work_pool_name
    worker_type = dummy_runner.worker_type

    try:
        deploy_and_run(flow, flow_id, work_pool_name, config, main_root)
    except ConnectError as e:
        print("Couldn't connect to server, attempting to start it now...")
        Server(["start"])
        Worker(
            [
                "start",
                "--name",
                "default",
                "--work_pool",
                work_pool_name,
                "--type",
                worker_type,
            ]
        )
        print("Trying to run flow again...")
        deploy_and_run(flow, flow_id, work_pool_name, config, main_root)
