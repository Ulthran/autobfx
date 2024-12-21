import networkx as nx
from pathlib import Path
from prefect import flow, tags
from autobfx.flows.fastqc import FASTQC
from autobfx.flows.heyfastq import HEYFASTQ
from autobfx.flows.trimmomatic import TRIMMOMATIC
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.utils import (
    gather_samples,
    get_input_fp,
    setup_step,
)


NAME = "qc"


def QC(config: Config, samples: dict[str, IOReads] = None) -> AutobfxFlow:
    project_fp = config.project_fp
    samples_list = (
        gather_samples(
            config.flows["trimmomatic"].get_input_reads(project_fp)[0],
            config.paired_end,
            config.samples,
        )
        if samples is None
        else samples
    )

    # Compose all the DAGs into one (without edges)
    trimmomatic_flow = TRIMMOMATIC(config, samples=samples_list)
    heyfastq_flow = HEYFASTQ(config, samples=samples_list)
    fastqc_flow = FASTQC(config, samples=samples_list)
    dag = nx.compose_all([trimmomatic_flow.dag, heyfastq_flow.dag, fastqc_flow.dag])

    # Map each trimmomatic task to the corresponding heyfastq and fastqc tasks (based on sample_name which is the only id attribute for all these tasks)
    for sample_name, _ in samples_list.items():
        dag.add_edge(
            [n for n in trimmomatic_flow.dag.nodes if n.ids == (sample_name,)][0],
            [n for n in heyfastq_flow.dag.nodes if n.ids == (sample_name,)][0],
        )
        dag.add_edge(
            [n for n in trimmomatic_flow.dag.nodes if n.ids == (sample_name,)][0],
            [n for n in fastqc_flow.dag.nodes if n.ids == (sample_name,)][0],
        )

    return AutobfxFlow(
        config,
        NAME,
        dag,
    )


@flow(name=NAME, log_prints=True)
def qc_flow(config: dict) -> list[Path]:
    submissions = [t.submit() for t in nx.topological_sort(QC(Config(**config)).dag)]
    return [s.result() for s in submissions]
