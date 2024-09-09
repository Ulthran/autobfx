import pytest
import sys
from prefect.testing.utilities import prefect_test_harness

sys.path.append(f"{__file__}/../../tasks")
sys.path.append(f"{__file__}/../../flows")
sys.path.append(f"{__file__}/../../utils")
sys.path.append(f"{__file__}/../../data_access")


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield
