import os
from pathlib import Path
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads


def run_fastqc(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
) -> Path:
    cmd = ["fastqc"]
    cmd += ["-o", str(output_reads[0].fp.parent)]
    cmd += (
        [str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else [str(input_reads[0].fp)]
    )
    cmd += ["-extract"]

    print(f"Running {' '.join(cmd)}")

    with ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"conda activate fastqc",
            " ".join(cmd),
        ],
        stream_output=False,
    ) as shell_operation:
        shell_process = shell_operation.trigger()
        shell_process.wait_for_completion()
        shell_output = shell_process.fetch_result()

    with open(log_fp, "w") as f:
        f.writelines(shell_output)

    return 1
