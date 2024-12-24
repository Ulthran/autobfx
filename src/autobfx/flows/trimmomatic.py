from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import AutobfxIterator
from autobfx.lib.task import AutobfxTask


NAME = "trimmomatic"


def TRIMMOMATIC(config: Config, sample_iterator: AutobfxIterator = None) -> AutobfxFlow:
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = AutobfxFlow.gather_samples(
        flow_config.get_input_reads(project_fp)[0],
        config.paired_end,
        config.samples,
        sample_iterator,
    )
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    sample_iterator = AutobfxIterator.gather(
        [{"sample": s} for s, _ in input_reads.items()], sample_iterator
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids=kvs,
            func=run_trimmomatic,
            project_fp=project_fp,
            input_reads=[input_reads[kvs["sample"]]],
            extra_inputs=extra_inputs,
            output_reads=[
                input_reads[kvs["sample"]].get_output_reads(output_reads[0]),
                input_reads[kvs["sample"]].get_output_reads(output_reads[1]),
            ],
            log_fp=log_fp / f"{kvs['sample']}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for kvs in sample_iterator
    ]

    return AutobfxFlow.from_tasks(NAME, tasks)
