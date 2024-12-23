import networkx as nx
from pathlib import Path
from prefect import flow
from autobfx.flows.qc import QC
from autobfx.flows.decontam import DECONTAM
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.iterator import SampleIterator, AutobfxIterator


NAME = "clean_shotgun"


def CLEAN_SHOTGUN(
    config: Config, samples: SampleIterator = None, hosts: AutobfxIterator = None
) -> AutobfxFlow:
    sample_iterator = SampleIterator.gather_samples(
        config.flows["trimmomatic"].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        samples,
    )
    host_iterator = AutobfxIterator.gather(
        "host",
        {
            x.stem: x.resolve()
            for x in Path(
                config.flows["align_to_host"].get_extra_inputs(config.project_fp)[
                    "hosts"
                ][0]
            ).glob("*.fasta")
        },
        hosts,
    )

    flow = AutobfxFlow.compose_flows(
        NAME,
        [
            QC(config, samples=sample_iterator),
            DECONTAM(config, samples=sample_iterator, hosts=host_iterator),
        ],
    )
    flow.connect_one_to_many(sample_iterator, "heyfastq", "align_to_host")

    return flow
