import os
from pathlib import Path
from autobfx.lib.utils import check_already_done
from autobfx.tasks.fastqc import run_fastqc


def test_fastqc(data_fp: Path, dummy_project_fp: Path, mocker):
    mocker.patch("prefect_shell.ShellOperation.run", return_value="FASTQC MOCKED")

    input_fp = data_fp / "reads" / "LONG_R1.fastq.gz"
    output_fp = dummy_project_fp / "fastqc" / "LONG_R1.fastq.gz"
    log_fp = dummy_project_fp / "logs" / "fastqc" / "LONG_R1.fastq.gz.log"

    os.makedirs(output_fp.parent, exist_ok=True)
    os.makedirs(log_fp.parent, exist_ok=True)

    assert (
        run_fastqc.fn(
            input_fp=input_fp,
            output_fp=output_fp,
            log_fp=log_fp,
        )
        == output_fp
    )

    assert check_already_done(output_fp)
    with open(log_fp) as f:
        assert f.read() == "FASTQC MOCKED"
