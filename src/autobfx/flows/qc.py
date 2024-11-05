import argparse
from pathlib import Path
from prefect import flow, tags
from prefect.deployments import run_deployment
from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.tasks.fastqc import run_fastqc
from autobfx.tasks.heyfastq import run_heyfastq
from autobfx.lib.config import Config, config_from_yaml
from autobfx.lib.utils import (
    gather_samples,
    get_input_fp,
    setup_step,
)


NAME = "qc"


@flow(name=NAME, log_prints=True)  # , task_runner=ThreadPoolTaskRunner(max_workers=5))
def qc_flow(
    project_fp: Path, config: Config, samples: dict[str, Path] = {}
) -> list[Path]:
    samples_list = (
        samples
        if samples
        else gather_samples(
            get_input_fp(Path(config.flows[NAME].input), project_fp),
            config.paired_end,
        )
    )

    # Setup
    trimmomatic_input_fp, trimmomatic_output_fp, trimmomatic_log_fp = setup_step(
        project_fp, config, "trimmomatic"
    )
    heyfastq_input_fp, heyfastq_output_fp, heyfastq_log_fp = setup_step(
        project_fp, config, "heyfastq"
    )
    fastqc_input_fp, fastqc_output_fp, fastqc_log_fp = setup_step(
        project_fp, config, "fastqc"
    )

    # Preprocess

    # Run
    results = {sample_name: {} for sample_name in samples_list.keys()}
    for sample_name, r1 in samples_list.items():
        with tags(sample_name):
            with tags("trimmomatic"):
                results[sample_name]["trimmomatic"] = run_trimmomatic.submit(
                    input_fp=r1,
                    output_fp=trimmomatic_output_fp / r1.name,
                    log_fp=trimmomatic_log_fp / f"{sample_name}.log",
                    env=config.flows["trimmomatic"].env,
                    paired_end=config.paired_end,
                    **config.flows["trimmomatic"].parameters,
                )

            with tags("heyfastq"):
                results[sample_name]["heyfastq"] = run_heyfastq.submit(
                    input_fp=r1,
                    output_fp=heyfastq_output_fp / r1.name,
                    log_fp=heyfastq_log_fp / f"{sample_name}.log",
                    paired_end=config.paired_end,
                    **config.flows["heyfastq"].parameters,
                    wait_for=[results[sample_name]["trimmomatic"]],
                )

            with tags("fastqc"):
                results[sample_name]["fastqc"] = run_fastqc.submit(
                    input_fp=r1,
                    output_fp=fastqc_output_fp / r1.name,
                    log_fp=fastqc_log_fp / f"{sample_name}.log",
                    env=config.flows["fastqc"].env,
                    paired_end=config.paired_end,
                    **config.flows["fastqc"].parameters,
                    wait_for=[results[sample_name]["trimmomatic"]],
                )

    # Postprocess

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run {NAME}")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    parser.add_argument(
        "--samples", nargs="*", default=[], help="Paths to samples to run"
    )
    args = parser.parse_args()
    config = config_from_yaml(Path(args.project_fp).absolute() / "config.yaml")

    samples = {}
    if args.samples:
        samples = {Path(sample).name: Path(sample).resolve() for sample in args.samples}

    # qc_flow(project_fp=Path(args.project_fp).absolute(), config=config, samples=samples)
    qc_flow.from_source(
        source=str(Path(__file__).parent),
        entrypoint="qc.py:qc_flow",
    ).deploy(
        name=f"{NAME}_deployment",
        work_pool_name="default",
        ignore_warnings=True,
    )

    run_deployment(
        f"{NAME}/{NAME}_deployment",
        parameters={
            "project_fp": Path(args.project_fp).absolute(),
            "config": config,
            "samples": samples,
        },
    )
