import argparse
import os
from pathlib import Path
from prefect import flow
from tasks.trimmomatic import run_trimmomatic
from tasks.lib.config import Config
from tasks.lib.utils import gather_samples


@flow(name="trimmomatic", log_prints=True)
def trimmomatic_flow(project_fp: Path, config: Config) -> list[Path]:
    flow_config = config.get_flow("trimmomatic")

    input_fp = Path(flow_config["input"])
    if not (
        input_fp.exists() and input_fp.is_dir() and len(list(input_fp.iterdir())) > 0
    ):
        input_fp = project_fp / flow_config["input"]
    if not (
        input_fp.exists() and input_fp.is_dir() and len(list(input_fp.iterdir())) > 0
    ):
        raise FileNotFoundError(
            f"Input directory {input_fp} does not exist or is empty"
        )

    output_fp = Path(flow_config["output"])
    if not output_fp.is_absolute():
        output_fp = project_fp / output_fp
    if not output_fp.exists():
        output_fp.mkdir(parents=True)

    log_fp = project_fp / "logs" / "trimmomatic"
    if not log_fp.exists():
        log_fp.mkdir(parents=True)

    adapter_template = (
        Path(os.environ.get("CONDA_PREFIX", ""))
        / "envs"
        / flow_config["env"]
        / "share/trimmomatic/adapters/NexteraPE-PE.fa"
    )

    # Check that flow doesn't already have a result

    # Preprocess

    # Run
    results = []
    for sample_name, r1 in gather_samples(
        input_fp, paired_end=config["paired_end"]
    ).items():
        print(sample_name, r1)
        results.append(
            run_trimmomatic.submit(
                input_fp=r1,
                output_fp=output_fp / r1.name,
                log_fp=log_fp / f"{sample_name}.log",
                paired_end=config["paired_end"],
                adapter_template=adapter_template,
                **flow_config.get("parameters", {}),
            )
        )

    # Postprocess

    return [r.result() for r in results]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run trimmomatic")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args()
    config = Config(Path(args.project_fp).absolute() / "config.yaml")
    print(config.get_flow("trimmomatic"))

    trimmomatic_flow(project_fp=Path(args.project_fp).absolute(), config=config)