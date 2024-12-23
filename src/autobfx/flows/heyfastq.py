import networkx as nx
from pathlib import Path
from prefect import flow
from autobfx.tasks.heyfastq import run_heyfastq
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import SampleIterator
from autobfx.lib.task import AutobfxTask


NAME = "heyfastq"


def HEYFASTQ(config: Config, samples: SampleIterator = None) -> AutobfxFlow:
    project_fp = config.project_fp
    flow_config = config.flows[NAME]
    input_reads = flow_config.get_input_reads(project_fp)
    output_reads = flow_config.get_output_reads(project_fp)
    log_fp = config.get_log_fp() / NAME
    runner = config.get_runner(flow_config)

    sample_iterator = SampleIterator.gather_samples(
        config.flows[NAME].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        samples,
    )

    tasks = [
        AutobfxTask(
            name=NAME,
            ids={"sample": sample_name},
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
        for sample_name, reads in sample_iterator
    ]

    dag = nx.DiGraph()
    for task in tasks:
        dag.add_node(task)

    return AutobfxFlow(NAME, dag)
