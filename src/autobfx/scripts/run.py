import argparse
import os
import yaml
from pathlib import Path
from autobfx import __version__


def main(argv):
    parser = argparse.ArgumentParser(description="Run a flow")
    parser.add_argument("flow", type=str, help="Name of the flow")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args(argv)

    project_fp = Path(args.project_fp).absolute()
    config_fp = project_fp / "config.yaml"

    print(
        "Don't use this, feature still in progress (/might not be the direction we wanna go)"
    )
