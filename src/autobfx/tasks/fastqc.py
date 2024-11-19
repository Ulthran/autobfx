from pathlib import Path
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner


def run_fastqc(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["fastqc"]
    cmd += ["-o", str(output_reads[0].fp.parent)]
    cmd += (
        [str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else [str(input_reads[0].fp)]
    )
    cmd += ["-extract"]
    cmd += ["2>&1", str(log_fp)]

    return runner.run_cmd(cmd)
