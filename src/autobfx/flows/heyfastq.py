import networkx as nx
from pathlib import Path
from prefect import flow
from autobfx.tasks.heyfastq import run_heyfastq
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.task import AutobfxTask
from autobfx.lib.utils import gather_samples


NAME = "heyfastq"


def HEYFASTQ(config: Config, samples: dict[str, IOReads] = None) -> AutobfxFlow:
    # TODO: Get rid of the samples argument, it's gross
    # Samples should probably be its own kind of Promise-esque class
    # that doesn't resolve until something gives it a value and then it keeps it
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    samples_list = (
        gather_samples(input_reads[0], config.paired_end, config.samples)
        if samples is None
        else samples
    )
    tasks = [
        AutobfxTask(
            name=NAME,
            ids=[sample_name],
            func=run_heyfastq,
            project_fp=project_fp,
            input_reads=[reads],
            output_reads=[reads.get_output_reads(output_reads[0])],
            log_fp=log_fp / f"{sample_name}.log",
            runner=runner,
            kwargs={
                **flow_config.parameters,
            },
        )
        for sample_name, reads in samples_list.items()
    ]

    dag = nx.DiGraph()
    for task in tasks:
        dag.add_node(task)

    return AutobfxFlow(config, NAME, dag)


@flow(name=NAME, log_prints=True)
def heyfastq_flow(config: dict) -> list[Path]:
    # Would love to use the flow object defined in the AutobfxFlow class
    # but we need a free standing @flow decorated function for the deployment
    # Do we go away from deployments?
    submissions = [
        t.submit() for t in nx.topological_sort(HEYFASTQ(Config(**config)).dag)
    ]
    return [s.result() for s in submissions]
