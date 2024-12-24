from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner
from pathlib import Path


def run_samtools_sort_sam(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["samtools", "view"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += ["-b", str(extra_inputs["sam"][0].fp)]
    cmd += ["|", "samtools", "sort"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += ["-o", str(extra_outputs["bam"][0].fp)]
    cmd += ["2>", str(log_fp)]

    runner.run_cmd(cmd)

    return cmd


def run_samtools_count_mapped_reads(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["samtools", "view"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += ["-c", "-F", "4"]
    cmd += [str(extra_inputs["bam"][0].fp)]
    cmd += [">", str(extra_outputs["count"][0].fp)]
    cmd += ["2>", str(log_fp)]

    runner.run_cmd(cmd)

    return cmd


def run_samtools_filter_mapped_reads(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["samtools", "view"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += ["-b", "-f", "12"]
    cmd += [str(extra_inputs["bam"][0].fp)]
    cmd += [">", str(extra_outputs["bam"][0].fp)]

    runner.run_cmd(cmd)

    return cmd


def run_samtools_merge_bams(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["samtools", "merge"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += [str(extra_outputs["bam"][0].fp)]
    for bam in extra_inputs["bams"]:
        cmd += [str(bam.fp)]
    cmd += ["2>", str(log_fp)]

    runner.run_cmd(cmd)

    return cmd


def run_samtools_bam_to_fastq(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    log_fp: Path,
    runner: AutobfxRunner,
):
    cmd = ["samtools", "fastq"]
    cmd += ["-@", str(runner.options["params"].threads)]
    cmd += ["-f", "12", "-c", "6"]  # Set compression level to 6 (standard for gzip)
    cmd += ["-1", str(extra_outputs["r1"][0].fp)]
    cmd += ["-2", str(extra_outputs["r2"][0].fp)]
    cmd += ["-0", "/dev/null"]  # READ1 and READ2 flags are the same
    cmd += ["-s", "/dev/null"]  # Singleton reads
    cmd += [str(extra_inputs["bam"][0].fp)]
    cmd += ["2>", str(log_fp)]

    runner.run_cmd(cmd)

    return cmd
