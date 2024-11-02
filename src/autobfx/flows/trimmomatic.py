import argparse
from pathlib import Path
from prefect import flow
from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.lib.config import Config
from autobfx.lib.utils import gather_samples, get_input_fp, get_log_fp, get_output_fp


NAME = "trimmomatic"


@flow(name=NAME, log_prints=True)
def trimmomatic_flow(
    project_fp: Path, config: Config, samples: dict[str, Path] = {}
) -> list[Path]:
    flow_config = config.flows[NAME]
    input_fp = get_input_fp(Path(flow_config.input), project_fp)
    output_fp = get_output_fp(Path(flow_config.output), project_fp)
    log_fp = get_log_fp(NAME, project_fp)

    # Preprocess

    # Run
    results = []
    samples_list = (
        samples if samples else gather_samples(input_fp, paired_end=config.paired_end)
    )
    for sample_name, r1 in samples_list.items():
        results.append(
            run_trimmomatic.submit(
                input_fp=r1,
                output_fp=output_fp / r1.name,
                log_fp=log_fp / f"{sample_name}.log",
                env=flow_config.env,
                paired_end=config.paired_end,
                **flow_config.parameters,
            )
        )

    # Postprocess

    return [r.result() for r in results]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run {NAME}")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    parser.add_argument(
        "--samples", nargs="*", default=[], help="Paths to samples to run"
    )
    args = parser.parse_args()
    config = Config(Path(args.project_fp).absolute() / "config.yaml")

    samples = {}
    if args.samples:
        samples = {Path(sample).name: Path(sample).resolve() for sample in args.samples}

    trimmomatic_flow(
        project_fp=Path(args.project_fp).absolute(), config=config, samples=samples
    )
