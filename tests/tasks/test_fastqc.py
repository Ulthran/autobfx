from autobfx.tasks.fastqc import run_fastqc


def test_fastqc():
    assert run_fastqc.fn() == "fastqc"
