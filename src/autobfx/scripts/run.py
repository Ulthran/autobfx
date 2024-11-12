import argparse
import os
from autobfx.lib.config import Config
from importlib.machinery import SourceFileLoader
from pathlib import Path


def main(argv):
    parser = argparse.ArgumentParser(description="Run a flow")
    parser.add_argument("flow", type=str, help="Name of the flow or path to the flow")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args(argv)

    project_fp = Path(args.project_fp).absolute()
    config_fp = project_fp / "config.py"

    os.makedirs(project_fp, exist_ok=True)
    os.makedirs(project_fp / ".autobfx" / "done", exist_ok=True)

    config_source = SourceFileLoader("config", str(config_fp)).load_module()
    config = Config(**config_source.config)

    from autobfx.flows import __dict__ as flows

    # TODO
    # Maybe require it to be input as "/path/to/flow.py:flow_name"
    # if Path(args.flow).exists():
    #    flow = SourceFileLoader("flow", args.flow).load_module()

    # TODO
    # Oof this one needs a lot of info too
    flow = flows[args.flow]
    flow.from_source(
        source=str(Path(__file__).parent),
        entrypoint="decontam.py:decontam_flow",
    ).deploy(
        name=f"{NAME}_deployment",
        work_pool_name="default",
        ignore_warnings=True,
    )

    run_deployment(
        f"{NAME}/{NAME}_deployment",
        parameters={
            "project_fp": Path(args.project_fp).absolute(),
            "config": config,
            "samples": samples,
        },
    )
