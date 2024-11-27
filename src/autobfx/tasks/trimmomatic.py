from pathlib import Path
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner


def run_trimmomatic(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
    threads: int = 1,
    leading: int = 3,
    trailing: int = 3,
    sw_start: int = 4,
    sw_end: int = 15,
    minlen: int = 36,
):
    try:
        adapter_template = extra_inputs["adapter_template"][0].fp
    except KeyError:
        adapter_template = None

    cmd = ["trimmomatic"]
    cmd += ["PE"] if input_reads[0].r2 else ["SE"]
    cmd += ["-threads", str(threads)]
    cmd += ["-phred33"]
    cmd += (
        [str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else [str(input_reads[0].fp)]
    )
    cmd += (
        [
            str(output_reads[0].fp),
            str(output_reads[1].fp),
            str(output_reads[0].r2),
            str(output_reads[1].r2),
        ]
        if input_reads[0].r2
        else [str(output_reads[0].fp)]
    )
    cmd += ["ILLUMINACLIP:" + str(adapter_template) + ":2:30:10:8:true"]
    cmd += ["LEADING:" + str(leading)]
    cmd += ["TRAILING:" + str(trailing)]
    cmd += ["SLIDINGWINDOW:" + str(sw_start) + ":" + str(sw_end)]
    cmd += ["MINLEN:" + str(minlen)]
    cmd += [">", str(log_fp), "2>&1"]

    runner.run_cmd(cmd)

    return 1
