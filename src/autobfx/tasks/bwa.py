from pathlib import Path
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner


def run_build_host_index(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
) -> Path:
    cmd = ["bwa", "index", str(extra_inputs["host"][0].fp), ">", str(log_fp), "2>&1"]

    runner.run_cmd(cmd)

    return 1


def run_align_to_host(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
    threads: int = 1,
) -> Path:
    cmd = ["bwa", "mem", "-M"]
    cmd += ["-t", str(threads)]
    cmd += [str(extra_inputs["host"][0].fp)]
    cmd += (
        [str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else [str(input_reads[0].fp)]
    )
    cmd += ["-o", str(output_reads[0].fp.parent)]
    cmd += [">", str(log_fp), "2>&1"]

    runner.run_cmd(cmd)

    return 1
