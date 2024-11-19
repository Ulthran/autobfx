from pathlib import Path
from autobfx.lib.config import Config
from autobfx.lib.io import IOReads
from autobfx.lib.runner import TestRunner
from autobfx.tasks.fastqc import run_fastqc


def test_fastqc(data_fp: Path, dummy_project: Config, test_runner: TestRunner):
    project_fp = dummy_project.project_fp
    input_reads = data_fp / "reads" / "LONG_R1.fastq.gz"
    output_reads = project_fp / "fastqc" / "LONG_R1.fastq.gz"
    log_fp = project_fp / "logs" / "fastqc" / "LONG_R1.fastq.gz.log"

    task = run_fastqc(
        input_reads=[IOReads(input_reads, IOReads.infer_r2(input_reads))],
        extra_inputs={},
        output_reads=[IOReads(output_reads, IOReads.infer_r2(output_reads))],
        extra_outputs={},
        log_fp=log_fp,
        runner=test_runner,
    )

    assert task[0] == "fastqc"
