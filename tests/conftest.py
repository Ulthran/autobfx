import pytest
from pathlib import Path


@pytest.fixture()
def data_fp() -> Path:
    return (Path(__file__).parent / "data").resolve()
