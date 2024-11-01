from src.autobfx.tasks.fastqc import run_fastqc


def test_fastqc(data_fp, test_project_fp):
    assert (
        run_fastqc.fn(
            input_fp=data_fp / "reads",
            output_fp=test_project_fp / "fastqc",
            log_fp=test_project_fp / "logs",
        )
        == test_project_fp / "fastqc"
    )
