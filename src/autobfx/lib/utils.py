import ast
from pathlib import Path
from autobfx.lib.config import Config, FlowConfig
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import AutobfxIterator


def get_input_fp(input_fp: Path, project_fp: Path) -> Path:
    if not (input_fp.exists() and input_fp.is_dir()):
        input_fp = project_fp / str(input_fp)
    if not (input_fp.exists() and input_fp.is_dir()):
        raise FileNotFoundError(f"Input directory {input_fp} does not exist")

    return input_fp


def get_output_fp(output_fp: Path, project_fp: Path) -> Path:
    if not output_fp.is_absolute():
        output_fp = project_fp / str(output_fp)
    if not output_fp.exists():
        output_fp.mkdir(parents=True)

    return output_fp


def get_log_fp(name: str, project_fp: Path) -> Path:
    log_fp = project_fp / "logs" / name
    if not log_fp.exists():
        log_fp.mkdir(parents=True)

    return log_fp


def check_already_done(output_fp: Path) -> bool:
    done_fp = output_fp.parent / f".{output_fp.name}.done"
    if done_fp.exists():
        print(f"Found {done_fp}")
        return True
    return False


def mark_as_done(output_fp: Path) -> None:
    done_fp = output_fp.parent / f".{output_fp.name}.done"
    done_fp.touch()


def setup_step(
    project_fp: Path, config: Config, step_name: str
) -> tuple[Path, Path, Path]:
    flow_config = config.flows[step_name]
    input_fp = get_input_fp(Path(flow_config.input), project_fp)
    output_fp = get_output_fp(Path(flow_config.output), project_fp)
    log_fp = get_log_fp(step_name, project_fp)

    return input_fp, output_fp, log_fp
