import os
from pathlib import Path
from prefect import task
from prefect_shell import ShellOperation


# TODO: Run this whenever a task fails to find conda env (instead of always running this as a check then create)
# This will be more efficient
@task
def create_environment(
    env_name: str,
    env_fp: Path,
    log_fp: Path,  # TODO: Consider but probably remove this, can just rely on task logs for this
) -> str:
    shell_output = ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"conda env create -f {env_fp} -n {env_name}",
        ]
    ).run()

    return shell_output
