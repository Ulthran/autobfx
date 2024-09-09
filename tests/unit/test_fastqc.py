from tasks.fastqc import fastqc


def test_fastqc():
    assert fastqc.fn() == "fastqc"
