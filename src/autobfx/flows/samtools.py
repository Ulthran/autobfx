from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.iterator import AutobfxIterator
from autobfx.tasks.samtools import run_samtools_sort_sam
from autobfx.lib.task import AutobfxTask


def SORT_SAM(
    config: Config,
    sample_iterator: AutobfxIterator = None,
    host_iterator: AutobfxIterator = None,
) -> AutobfxFlow:
    NAME = "sort_sam"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = AutobfxFlow.gather_samples(
        flow_config.get_input_reads(project_fp)[0],
        config.paired_end,
        config.samples,
        sample_iterator,
    )
    extra_inputs = AutobfxFlow.gather_files(
        flow_config.get_extra_inputs(project_fp)["sams"][0], "sam", host_iterator
    )
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    host_iterator = AutobfxIterator.gather(
        {"host": host_name for host_name in extra_inputs.keys()},
        host_iterator,
    )
    sample_iterator = AutobfxIterator.gather(
        [{"sample": s} for s, _ in input_reads.items()], sample_iterator
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids=kvs,
            func=run_samtools_sort_sam,
            project_fp=config.project_fp,
            extra_inputs={
                "sams": [
                    extra_outputs["sams"][0] / f"{kvs['host']}_{kvs['sample']}.sam"
                ]
            },
            extra_outputs={
                "bams": [
                    extra_outputs["bams"][0] / f"{kvs['host']}_{kvs['sample']}.bam"
                ]
            },
            log_fp=log_fp / f"{kvs['host']}_{kvs['sample']}.log",
            runner=runner,
            kwargs={
                **config.flows[NAME].parameters,
            },
        )
        for kvs in AutobfxIterator.expand([sample_iterator, host_iterator])
    ]

    return AutobfxFlow.from_tasks(NAME, tasks)
