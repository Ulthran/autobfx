import os
import pytest
import sys
from pathlib import Path
#from autobfx.scripts.init import main as Init

# Ensure 'src' is in the Python path for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture()
def data_fp() -> Path:
    return (Path(__file__).parent / "data").resolve()

"""
@pytest.fixture()
def dummy_project_fp(data_fp: Path, tmp_path: Path) -> Path:
    project_fp = tmp_path / "projects" / "test"
    config = Init([str(project_fp)])
    config.flows["trimmomatic"].input = data_fp / "reads"
    config.config_to_yaml(project_fp / "config.yaml")

    return project_fp
"""