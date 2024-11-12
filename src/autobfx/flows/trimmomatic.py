import argparse
from importlib.machinery import SourceFileLoader
from pathlib import Path
from prefect import flow
from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.lib.config import Config
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.task import AutobfxTask
from autobfx.lib.utils import gather_samples, get_input_fp, get_log_fp, get_output_fp


NAME = "trimmomatic"


@flow(name=NAME, log_prints=True)
def trimmomatic_flow(config: Config) -> list[Path]:
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME

    # Preprocess

    # Run
    samples_list = gather_samples(input_reads[0], config.paired_end, config.samples)
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=[NAME, sample_name],
            func=run_trimmomatic,
            project_fp=project_fp,
            input_reads=[reads],
            output_reads=[
                reads.get_output_reads(output_reads[0]),
                reads.get_output_reads(output_reads[1]),
            ],
            log_fp=log_fp / f"{sample_name}.log",
            kwargs={
                # "conda_env": flow_config.conda,
                # "paired_end": config.paired_end,
                **flow_config.parameters,
            },
        )
        for sample_name, reads in samples_list.items()
    ]
    submissions = [task.submit() for task in tasks]

    # Postprocess

    return [s.result() for s in submissions]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run {NAME}")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args()

    config_source = SourceFileLoader(
        "config", str(Path(args.project_fp).absolute() / "config.py")
    ).load_module()
    config = Config(**config_source.config)

    trimmomatic_flow(config)
