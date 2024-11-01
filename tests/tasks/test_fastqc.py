import os
from pathlib import Path
from autobfx.tasks.fastqc import run_fastqc


def test_fastqc(data_fp: Path, dummy_project_fp: Path):
    os.makedirs(dummy_project_fp / "fastqc", exist_ok=True)
    os.makedirs(dummy_project_fp / "logs" / "fastqc", exist_ok=True)

    assert (
        run_fastqc.fn(
            input_fp=data_fp / "reads" / "LONG_R1.fastq.gz",
            output_fp=dummy_project_fp / "fastqc" / "LONG_R1.fastq.gz",
            log_fp=dummy_project_fp / "logs" / "fastqc" / "LONG_R1.fastq.gz.log",
        )
        == dummy_project_fp / "fastqc" / "LONG_R1.fastq.gz"
    )
