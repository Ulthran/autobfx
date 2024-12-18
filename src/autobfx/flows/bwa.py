from pathlib import Path
from prefect import flow
from autobfx.tasks.bwa import run_align_to_host, run_build_host_index
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.task import AutobfxTask
from autobfx.lib.utils import gather_samples


def BUILD_HOST_INDEX(config: Config, hosts: dict[str, Path] = None) -> AutobfxFlow:
    NAME = "build_host_index"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    hosts_list = (
        {x.stem: x.resolve() for x in Path(extra_inputs["hosts"][0]).glob("*.fasta")}
        if hosts is None
        else hosts
    )
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=[host_name],
            func=run_build_host_index,
            project_fp=project_fp,
            extra_inputs={"host": [fa]},
            extra_outputs={
                "host_indices": [
                    extra_outputs["host_indices"][0] / f"{host_name}.fasta.{index}"
                    for index in ["amb", "ann", "bwt", "pac", "sa"]
                ]
            },
            log_fp=log_fp / f"{host_name}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for host_name, fa in hosts_list.items()
    ]

    return AutobfxFlow(config, NAME, tasks)


def ALIGN_TO_HOST(
    config: Config, samples: dict[str, IOReads] = None, hosts: dict[str, Path] = None
) -> AutobfxFlow:
    NAME = "align_to_host"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    hosts_list = (
        {x.stem: x.resolve() for x in Path(extra_inputs["hosts"][0]).glob("*.fasta")}
        if hosts is None
        else hosts
    )
    samples_list = (
        gather_samples(input_reads[0], config.paired_end, config.samples)
        if samples is None
        else samples
    )
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=[sample_name, host_name],
            func=run_align_to_host,
            project_fp=project_fp,
            input_reads=[reads],
            extra_inputs={"host": [fa]},
            extra_outputs={
                "sams": [extra_outputs["sams"][0] / f"{host_name}_{sample_name}.sam"]
            },
            log_fp=log_fp / f"{sample_name}_{host_name}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for sample_name, reads in samples_list.items()
        for host_name, fa in hosts_list.items()
    ]

    return AutobfxFlow(config, NAME, tasks)


@flow(name="build_host_index", log_prints=True)
def build_host_index_flow(config: dict) -> list[Path]:
    submissions = [task.submit() for task in BUILD_HOST_INDEX(Config(**config)).tasks]
    return [s.result() for s in submissions]


@flow(name="align_to_host", log_prints=True)
def align_to_host_flow(config: Config) -> list[Path]:
    submissions = [task.submit() for task in ALIGN_TO_HOST(config).tasks]
    return [s.result() for s in submissions]
