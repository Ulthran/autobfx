from pathlib import Path
from prefect import flow
from autobfx.tasks.heyfastq import run_heyfastq
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.task import AutobfxTask
from autobfx.lib.utils import gather_samples


NAME = "heyfastq"


def HEYFASTQ(config: Config) -> AutobfxFlow:
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME

    # Preprocess

    # Run
    samples_list = gather_samples(input_reads[0], config.paired_end, config.samples)
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=[NAME, sample_name],
            func=run_heyfastq,
            project_fp=project_fp,
            input_reads=[reads],
            output_reads=[reads.get_output_reads(output_reads[0])],
            log_fp=log_fp / f"{sample_name}.log",
            # runner=flow_config.runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for sample_name, reads in samples_list.items()
    ]

    return AutobfxFlow(config, NAME, tasks)


@flow(name=NAME, log_prints=True)
def heyfastq_flow(config: dict) -> list[Path]:
    submissions = [task.submit() for task in HEYFASTQ(Config(**config)).tasks]
    return [s.result() for s in submissions]
