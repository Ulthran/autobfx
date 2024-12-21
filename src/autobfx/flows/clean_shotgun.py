import networkx as nx
from pathlib import Path
from prefect import flow
from autobfx.flows.qc import QC
from autobfx.flows.decontam import DECONTAM
from autobfx.flows.bwa import BUILD_HOST_INDEX, ALIGN_TO_HOST
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.utils import (
    gather_samples,
)


def CLEAN_SHOTGUN(config: Config) -> AutobfxFlow:
    NAME = "clean_shotgun"
    project_fp = config.project_fp
    hosts_list = {
        x.stem: x.resolve()
        for x in Path(
            config.flows["build_host_index"].get_extra_inputs(project_fp)["hosts"][0]
        ).glob("*.fasta")
    }
    samples_list = gather_samples(
        config.flows["trimmomatic"].get_input_reads(project_fp)[0],
        config.paired_end,
        config.samples,
    )

    # TODO: Can we create AutobfxIterator and AutobfxConnector classes to handle all this and have a cleaner API?
    # We should be able to
    # 1) Automatically generate singleton flows for a single task (over a set of iterators)
    # 2) Easily connect to flows to create another
    # Also though, this isn't bad for now, it's a bit complicated for a first layer of abstraction on custom flows
    # but it's pretty good, we should focus on other things for now to get this into actual test environments

    qc_flow = QC(config, samples=samples_list)
    build_host_index_flow = BUILD_HOST_INDEX(config, hosts=hosts_list)
    align_to_host_flow = ALIGN_TO_HOST(config, samples=samples_list, hosts=hosts_list)
    dag = nx.compose_all(
        [qc_flow.dag, build_host_index_flow.dag, align_to_host_flow.dag]
    )

    # Add dependencies between align_to_host and build_host_index tasks
    for host_name, _ in hosts_list.items():
        for align_to_host_task in [
            n for n in align_to_host_flow.dag.nodes if host_name in n.ids
        ]:
            dag.add_edge(
                [n for n in build_host_index_flow.dag.nodes if n.ids == (host_name,)][
                    0
                ],
                align_to_host_task,
            )

    # Add dependencies between align_to_host and qc tasks
    for sample_name, _ in samples_list.items():
        for align_to_host_task in [
            n for n in align_to_host_flow.dag.nodes if sample_name in n.ids
        ]:
            dag.add_edge(
                [
                    n
                    for n in qc_flow.dag.nodes
                    if n.ids == (sample_name,) and n.name == "heyfastq"
                ][0],
                align_to_host_task,
            )

    return AutobfxFlow(
        config,
        NAME,
        dag,
    )


@flow(name="clean_shotgun", log_prints=True)
def clean_shotgun_flow(config: dict) -> list[Path]:
    # TODO: Fix this, should be submitting here not in CLEAN_SHOTGUN
    # Need to pass wait_for to here somehow, adjust AutobfxFlow to accept
    submissions = [t.submit() for t in CLEAN_SHOTGUN(Config(**config)).tasks]
    return [s.result() for s in submissions]
