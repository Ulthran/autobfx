import argparse
import os
from autobfx.lib.config import Config, FlowConfig
from autobfx.scripts.server import main as Server
from autobfx.scripts.worker import main as Worker
from httpx import ConnectError
from importlib.machinery import SourceFileLoader
from prefect.client.schemas import FlowRun
from prefect.deployments import run_deployment
from prefect.exceptions import ObjectNotFound
from pathlib import Path


def deploy_and_run(
    flow: callable,
    flow_id: str,
    work_pool_name: str,
    config: Config,
    main_root: Path,
    update_deployment: bool = False,
):
    # if update_deployment or os.environ.get("AUTOBFX_DEBUG", False):
    # TODO: Silence this, probably in a context manager setting stdout/stderr to /dev/null
    flow.from_source(
        source=str(main_root),
        entrypoint=f"{flow_id.split(':')[0]}.py:{flow_id.split(':')[1]}",
    ).deploy(
        name=f"{flow_id}_deployment",
        work_pool_name=work_pool_name,
        ignore_warnings=True,
    )

    print("Submitting flow...")
    try:
        run_deployment(
            f"{flow_id.split(':')[0]}/{flow_id}_deployment",
            parameters={
                "config": config.dict(),
            },
        )
        print("Success!")
    except KeyError as e:
        print(f"It's likely you provided a flow that doesn't exist: {e}")
    except ObjectNotFound as e:
        print(
            f"It's likely you provided a flow that hasn't been deployed (try re-running with '--update_deployment'): {e}"
        )


def main(argv) -> FlowRun:
    parser = argparse.ArgumentParser(description="Run a flow")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    parser.add_argument("flow", type=str, help="The flow to run")
    parser.add_argument(
        "--update_deployment", action="store_true", help="Update the deployment"
    )

    args = parser.parse_args(argv)

    project_fp = Path(args.project_fp).absolute()
    flow_id = args.flow

    os.makedirs(project_fp, exist_ok=True)

    config_source = SourceFileLoader(
        "config", str(Path(args.project_fp).absolute() / "config.py")
    ).load_module()
    config = Config(**config_source.config)

    from autobfx.flows.bwa import ALIGN_TO_HOST, BUILD_HOST_INDEX
    from autobfx.flows.clean_shotgun import CLEAN_SHOTGUN
    from autobfx.flows.decontam import DECONTAM
    from autobfx.flows.qc import QC
    from autobfx.flows.trimmomatic import TRIMMOMATIC

    # ALIGN_TO_HOST(config).run()
    CLEAN_SHOTGUN(config).run()
    # DECONTAM(config).run()
    # QC(config).run()
    # TRIMMOMATIC(config).run()
    return

    from autobfx.flows import flows
    from autobfx.flows import root as main_root

    # TODO Once we have plugins they should be imported here (somehow find all 'autobfx-...' packages and import __dict__) (or more likely build some sort of registry object that they can poke on install)
    # Is this also the place to update the runner_map if it needs it?

    try:
        flow = flows[flow_id]
    except KeyError:
        raise KeyError(f"Flow '{flow_id}' not found in: {flows.keys()}")

    dummy_runner = config.get_runner(FlowConfig())
    work_pool_name = dummy_runner.work_pool_name
    worker_type = dummy_runner.worker_type

    try:
        deploy_and_run(
            flow,
            flow_id,
            work_pool_name,
            config,
            main_root,
            update_deployment=args.update_deployment,
        )
    except ConnectError:
        print("Couldn't connect to server, attempting to start it now...")
        Server(["start"])
        if not Worker(["status", "--work_pool", work_pool_name]):
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
        deploy_and_run(
            flow,
            flow_id,
            work_pool_name,
            config,
            main_root,
            update_deployment=args.update_deployment,
        )
    except ValueError as e:
        if "Could not find work pool" in str(e):
            print("Couldn't find work pool, attempting to start worker now...")
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
            deploy_and_run(
                flow,
                flow_id,
                work_pool_name,
                config,
                main_root,
                update_deployment=args.update_deployment,
            )
