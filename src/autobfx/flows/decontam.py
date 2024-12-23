import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import AutobfxIterator, SampleIterator
from autobfx.flows.bwa import ALIGN_TO_HOST, BUILD_HOST_INDEX
from pathlib import Path


NAME = "decontam"


def DECONTAM(
    config: Config, samples: SampleIterator = None, hosts: AutobfxIterator = None
) -> AutobfxFlow:
    sample_iterator = SampleIterator.gather_samples(
        config.flows["align_to_host"].get_input_reads(config.project_fp)[0],
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
            BUILD_HOST_INDEX(config, hosts=host_iterator),
            ALIGN_TO_HOST(config, samples=sample_iterator, hosts=host_iterator),
        ],
    )
    flow.connect_one_to_many(host_iterator, "build_host_index", "align_to_host")

    return flow
