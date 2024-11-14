from pathlib import Path
from prefect import flow
from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.task import AutobfxTask
from autobfx.lib.utils import gather_samples


NAME = "trimmomatic"


def TRIMMOMATIC(config: Config) -> AutobfxFlow:
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME

    samples_list = gather_samples(input_reads[0], config.paired_end, config.samples)
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=(sample_name),
            func=run_trimmomatic,
            project_fp=project_fp,
            input_reads=[reads],
            extra_inputs=extra_inputs,
            output_reads=[
                reads.get_output_reads(output_reads[0]),
                reads.get_output_reads(output_reads[1]),
            ],
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
def trimmomatic_flow(config: dict) -> list[Path]:
    submissions = [task.submit() for task in TRIMMOMATIC(Config(**config)).tasks]
    return [s.result() for s in submissions]
