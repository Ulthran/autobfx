from pathlib import Path
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner


def run_heyfastq(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
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
    cmd += ["2>&1", str(log_fp)]

    runner.run_cmd(cmd)

    return 1
