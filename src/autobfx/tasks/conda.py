import os
from pathlib import Path
from prefect import task
from prefect_shell import ShellOperation


@task
def create_environment(
    env_name: str,
    env_fp: Path,
    log_fp: Path,
) -> str:
    shell_output = ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"conda env create -f {env_fp} -n {env_name}",
        ]
    ).run()

    return shell_output
