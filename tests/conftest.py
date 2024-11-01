import pytest
from pathlib import Path
from src.autobfx.lib.config import Config, config_to_yaml
from src.autobfx.scripts.init import main as Init


@pytest.fixture()
def data_fp() -> Path:
    return (Path(__file__).parent / "data").resolve()


@pytest.fixture()
def test_project_fp(data_fp) -> Path:
    project_fp = data_fp / "projects" / "test"
    Init(str(project_fp))
