from pathlib import Path
from autobfx.tasks.fastqc import run_fastqc


def test_fastqc(data_fp: Path, dummy_project_fp: Path):
    assert (
        run_fastqc.fn(
            input_fp=data_fp / "reads",
            output_fp=dummy_project_fp / "fastqc",
            log_fp=dummy_project_fp / "logs",
        )
        == dummy_project_fp / "fastqc"
    )
