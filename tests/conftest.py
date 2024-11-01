import pytest
from pathlib import Path
from prefect.testing.utilities import prefect_test_harness


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


@pytest.fixture(autouse=True, scope="session")
def data_fp():
    return Path("data/").resolve()