from pathlib import Path
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads


def run_heyfastq(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    sub_cmd: str = "filter-kscore",
    min_kscore: float = 0.5,
) -> Path:
    # TODO: Just use the python API instead of the shell command
    cmd = ["heyfastq", sub_cmd]
    cmd += (
        ["--input", str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else ["--input", str(input_reads[0].fp)]
    )
    cmd += (
        ["--output", str(output_reads[0].fp), str(output_reads[0].r2)]
        if input_reads[0].r2
        else ["--output", str(output_reads[0].fp)]
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
