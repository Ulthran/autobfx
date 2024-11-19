import pytest
import shutil
from pathlib import Path
from src.autobfx.scripts.init import main as Init

# Ensure 'src' is in the Python path for package imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture()
def data_fp() -> Path:
    return (Path(__file__).parent / "data").resolve()


@pytest.fixture()
def dummy_project_fp(data_fp: Path, tmp_path: Path) -> Path:
    project_fp = tmp_path / "projects" / "test"
    shutil.copytree(data_fp / "example_project", project_fp)

    return project_fp
