import ast
from pathlib import Path
from autobfx.lib.config import Config, FlowConfig
from autobfx.lib.io import IOReads


def gather_samples(
    fp: Path, paired_end: bool, samples: dict[str, str | Path]
) -> dict[str, IOReads]:
    if samples:
        return {n: IOReads(fp) for n, fp in samples.items()}
    if paired_end:
        r1 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R1" in x.name]
        r2 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R2" in x.name]
        sample_names = [x.name.split("_R1")[0] for x in r1]
        sample_names_2 = [x.name.split("_R2")[0] for x in r2]
        if sample_names != sample_names_2:
            print(sample_names)
            print(sample_names_2)
            raise ValueError(f"Sample names do not match in {fp}")
        if len(sample_names) != len(set(sample_names)):
            print(sample_names)
            raise ValueError(
                f"Duplicate sample names in {fp} (Only what's in front of '_R1'/'_R2' is considered)"
            )

        if len(r1) != len(r2):
            print(r1)
            print(r2)
            raise ValueError(f"Number of R1 and R2 files do not match in {fp}")

        return {x: IOReads(y, z) for x, y, z in zip(sample_names, r1, r2)}
    else:
        r1 = list(fp.glob("*.fastq.gz"))
        sample_names = [x.name.split(".fastq")[0] for x in r1]
        if len(sample_names) != len(set(sample_names)):
            print(sample_names)
            raise ValueError(f"Duplicate sample names in {fp}")

        return {x: IOReads(y) for x, y in zip(sample_names, r1)}


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
