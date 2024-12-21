import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.flows.bwa import ALIGN_TO_HOST, BUILD_HOST_INDEX
from autobfx.lib.utils import gather_samples
from pathlib import Path
from prefect import flow


NAME = "decontam"


def DECONTAM(
    config: Config, samples: dict[str, IOReads] = None, hosts: dict[str, Path] = None
) -> AutobfxFlow:
    project_fp = config.project_fp
    samples_list = (
        gather_samples(
            config.flows["qc"].get_input_reads(project_fp)[0],
            config.paired_end,
            config.samples,
        )
        if samples is None
        else samples
    )
    hosts_list = (
        {
            x.stem: x.resolve()
            for x in Path(
                config.flows["align_to_host"].get_extra_inputs(project_fp)["hosts"][0]
            ).glob("*.fasta")
        }
        if hosts is None
        else hosts
    )

    build_host_index_flow = BUILD_HOST_INDEX(config, hosts=hosts_list)
    align_to_host_flow = ALIGN_TO_HOST(config, samples=samples_list, hosts=hosts_list)
    dag = nx.compose_all([build_host_index_flow.dag, align_to_host_flow.dag])

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

    return AutobfxFlow(config, NAME, dag)
