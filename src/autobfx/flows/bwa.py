from pathlib import Path
from autobfx.tasks.bwa import run_align_to_host, run_build_host_index
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.iterator import AutobfxIterator
from autobfx.lib.task import AutobfxTask


def BUILD_HOST_INDEX(
    config: Config, host_iterator: AutobfxIterator = None
) -> AutobfxFlow:
    NAME = "build_host_index"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    extra_inputs = AutobfxFlow.gather_files(
        flow_config.get_extra_inputs(project_fp)["hosts"][0], "fasta", host_iterator
    )
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    host_iterator = AutobfxIterator.gather(
        [{"host": host_name} for host_name in extra_inputs.keys()],
        host_iterator,
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids=kvs,
            func=run_build_host_index,
            project_fp=project_fp,
            extra_inputs={"host": [extra_inputs[kvs["host"]]]},
            extra_outputs={
                "host_indices": [
                    extra_outputs["host_indices"][0] / f"{kvs['host']}.fasta.{index}"
                    for index in ["amb", "ann", "bwt", "pac", "sa"]
                ]
            },
            log_fp=log_fp / f"{kvs['host']}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for kvs in host_iterator
    ]

    return AutobfxFlow.from_tasks(NAME, tasks)


def ALIGN_TO_HOST(
    config: Config,
    sample_iterator: AutobfxIterator = None,
    host_iterator: AutobfxIterator = None,
) -> AutobfxFlow:
    NAME = "align_to_host"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = AutobfxFlow.gather_samples(
        flow_config.get_input_reads(project_fp)[0],
        config.paired_end,
        config.samples,
        sample_iterator,
    )
    extra_inputs = AutobfxFlow.gather_files(
        flow_config.get_extra_inputs(project_fp)["hosts"][0], "fasta", host_iterator
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
    print(extra_inputs)
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=kvs,
            func=run_align_to_host,
            project_fp=project_fp,
            input_reads=[input_reads[kvs["sample"]]],
            extra_inputs={"host": [extra_inputs[kvs["host"]]]},
            extra_outputs={
                "sams": [
                    extra_outputs["sams"][0] / f"{kvs['host']}_{kvs['sample']}.sam"
                ]
            },
            log_fp=log_fp / f"{kvs['host']}_{kvs['sample']}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for kvs in AutobfxIterator.expand([sample_iterator, host_iterator])
    ]

    return AutobfxFlow.from_tasks(NAME, tasks)
