import networkx as nx
from pathlib import Path
from prefect import flow
from autobfx.tasks.bwa import run_align_to_host, run_build_host_index
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.iterator import AutobfxIterator, SampleIterator
from autobfx.lib.task import AutobfxTask


def BUILD_HOST_INDEX(config: Config, hosts: AutobfxIterator = None) -> AutobfxFlow:
    NAME = "build_host_index"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    host_iterator = AutobfxIterator.gather(
        "host",
        {x.stem: x.resolve() for x in Path(extra_inputs["hosts"][0]).glob("*.fasta")},
        hosts,
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids={"host": host_name},
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
        for host_name, fa in host_iterator
    ]

    dag = nx.DiGraph()
    for task in tasks:
        dag.add_node(task)

    return AutobfxFlow(NAME, dag)


def ALIGN_TO_HOST(
    config: Config, samples: SampleIterator = None, hosts: AutobfxIterator = None
) -> AutobfxFlow:
    NAME = "align_to_host"
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    extra_inputs = flow_config.get_extra_inputs(project_fp)
    extra_outputs = flow_config.get_extra_outputs(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    host_iterator = AutobfxIterator.gather(
        "host",
        {x.stem: x.resolve() for x in Path(extra_inputs["hosts"][0]).glob("*.fasta")},
        hosts,
    )
    sample_iterator = SampleIterator.gather_samples(
        config.flows[NAME].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        samples,
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids={"sample": sample_name, "host": host_name},
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
        for sample_name, reads in sample_iterator
        for host_name, fa in host_iterator
    ]

    dag = nx.DiGraph()
    for task in tasks:
        dag.add_node(task)

    return AutobfxFlow(NAME, dag)
