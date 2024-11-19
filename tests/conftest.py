import pytest
import shutil
from importlib.machinery import SourceFileLoader
from pathlib import Path
from src.autobfx.lib.config import Config
from src.autobfx.lib.runner import TestRunner
from src.autobfx.scripts.init import main as Init


@pytest.fixture()
def data_fp() -> Path:
    return (Path(__file__).parent / "data").resolve()


@pytest.fixture()
def dummy_project(data_fp: Path, tmp_path: Path) -> Config:
    project_fp = tmp_path / "projects" / "test"
    shutil.copytree(data_fp / "example_project", project_fp)

    config_source = SourceFileLoader(
        "config", str(project_fp / "config.py")
    ).load_module()
    config = Config(**config_source.config)

    return config


@pytest.fixture
def test_runner() -> TestRunner:
    def run_cmd(cmd: list[str], opts: dict = {}):
        print(" ".join(cmd))
        return cmd

    def run_func(func: callable, args: list, kwargs: dict, opts: dict = {}):
        print(f"Running {func.__name__} with args {args} and kwargs {kwargs}")
        return func

    return TestRunner(run_cmd=run_cmd, run_func=run_func)
