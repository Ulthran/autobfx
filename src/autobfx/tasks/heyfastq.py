from pathlib import Path
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads


def run_heyfastq(
    input_reads: list[IOReads],
    extra_inputs: dict[str, IOObject],
    output_reads: list[IOReads],
    extra_outputs: dict[str, IOObject],
    log_fp: Path,
    sub_cmd: str = "filter-kscore",
    min_kscore: float = 0.5,
) -> Path:
    r1_in = input_reads[0].fp
    r2_in = input_reads[0].r2
    paired_end = r2_in is not None
    r1_out = output_reads[0].fp
    r2_out = output_reads[0].r2

    # TODO: Just use the python API instead of the shell command
    # Create command
    cmd = ["heyfastq", sub_cmd]
    cmd += (
        ["--input", str(r1_in), str(r2_in)] if paired_end else ["--input", str(r1_in)]
    )
    cmd += (
        ["--output", str(r1_out), str(r2_out)]
        if paired_end
        else ["--output", str(r1_out)]
    )
    cmd += ["--min-kscore", str(min_kscore)]

    print(f"Running {' '.join(cmd)}")

    with ShellOperation(
        commands=[
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
