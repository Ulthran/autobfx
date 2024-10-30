import os
from pathlib import Path
from prefect import task
from prefect_shell import ShellOperation


@task
def run_fastqc(
    input_fp: Path,
    output_fp: Path,
    log_fp: Path,
    paired_end: bool = True,
) -> Path:
    # Check files
    if not input_fp.exists():
        raise FileNotFoundError(f"Input file not found: {input_fp}")
    if paired_end:
        input_pair_fp = Path(str(input_fp).replace("_R1", "_R2"))
        if not input_pair_fp.exists():
            raise FileNotFoundError(f"Paired-end file not found: {input_pair_fp}")

    # Create command
    cmd = ["fastqc"]
    cmd += ["-o", str(output_fp)]
    cmd += [str(input_fp), str(input_pair_fp)] if paired_end else [str(input_fp)]
    cmd += ["-extract"]

    # Run command
    shell_output = ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            "conda activate fastqc",
            " ".join(cmd),
        ]
    ).run()

    with open(log_fp, "w") as f:
        # Consider using sp.Popen for finer control over running process
        # sp.run(cmd, shell=True, executable="/bin/bash", stdout=f, stderr=f)
        f.writelines(shell_output)

    return output_fp
