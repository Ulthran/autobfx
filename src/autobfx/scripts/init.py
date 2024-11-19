import argparse
import os
from pathlib import Path
from autobfx import __version__
from autobfx.lib.config import Config, FlowConfig


def default_config(project_fp: Path, name: str = None) -> Config:
    return Config(
        version=__version__,
        name=name if name else project_fp.name,
        project_fp=project_fp,
        paired_end=True,
        log_dir="logs",
        flows={
            "trimmomatic": FlowConfig(
                input="reads",
                output="trimmomatic",
                env="trimmomatic",
                parameters={"threads": 4},
            ),
            "fastqc": FlowConfig(
                input="trimmomatic",
                output="fastqc",
                env="fastqc",
            ),
            "heyfastq": FlowConfig(
                input="fastqc",
                output="heyfastq",
            ),
        },
    )


def main(argv):
    print("NOT IMPLEMENTED YET")
    print("Not sure we're going to have this, probably will, but not sure")

    parser = argparse.ArgumentParser(description="Initialize a new project")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args(argv)

    project_fp = Path(args.project_fp).absolute()
    config_fp = project_fp / "config.py"

    os.makedirs(project_fp, exist_ok=True)
    os.makedirs(project_fp / ".autobfx" / "done", exist_ok=True)

    config = default_config(project_fp)
    config.config_to_py(config_fp)  # TODO

    print(f"Created project at {project_fp}")

    return config
