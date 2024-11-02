import argparse
import asyncio
from pathlib import Path
from prefect import flow
from prefect.deployments import run_deployment
from prefect.task_runners import ThreadPoolTaskRunner
from ..flows.trimmomatic import trimmomatic_flow
from ..flows.fastqc import fastqc_flow
from ..flows.heyfastq import heyfastq_flow
from ..lib.config import Config, config_from_yaml
from ..lib.utils import gather_samples, get_input_fp


NAME = "qc"


@flow(name=NAME, log_prints=True, task_runner=ThreadPoolTaskRunner(max_workers=5))
def qc_flow(
    project_fp: Path, config: Config, samples: dict[str, Path] = {}
) -> list[Path]:
    samples_list = (
        samples
        if samples
        else gather_samples(
            get_input_fp(Path(config.flows["trimmomatic"].input), project_fp),
            config.paired_end,
        )
    )
    results = {sample_name: {} for sample_name in samples_list.keys()}

    async def qc_for_sample(sample_name, r1):
        results[sample_name]["trimmomatic"] = trimmomatic_flow(
            project_fp, config, samples={sample_name: r1}
        )
        results[sample_name]["heyfastq"] = heyfastq_flow(
            project_fp, config, samples={sample_name: r1}
        )
        results[sample_name]["fastqc"] = fastqc_flow(
            project_fp, config, samples={sample_name: r1}
        )

    async def submit_flows():
        await asyncio.gather(
            *[
                qc_for_sample(sample_name, r1)
                for sample_name, r1 in samples_list.items()
            ]
        )

    asyncio.run(submit_flows())

    print(results)
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
