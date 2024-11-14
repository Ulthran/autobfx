import os
from pathlib import Path
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads


def run_fastqc(
    input_reads: list[IOReads],
    extra_inputs: dict[str, IOObject],
    output_reads: list[IOReads],
    extra_outputs: dict[str, IOObject],
    log_fp: Path,
) -> Path:
    r1_in = input_reads[0].fp
    r2_in = input_reads[0].r2
    paired_end = r2_in is not None
    r1_out = output_reads[0].fp
    r2_out = output_reads[0].r2

    # Create command
    cmd = ["fastqc"]
    cmd += ["-o", str(r1_out.parent)]
    cmd += [str(r1_in), str(r2_in)] if paired_end else [str(r1_in)]
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
