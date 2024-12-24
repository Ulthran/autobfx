import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import AutobfxIterator
from autobfx.flows.bwa import ALIGN_TO_HOST, BUILD_HOST_INDEX
from autobfx.flows.samtools import SORT_SAM
from pathlib import Path


NAME = "decontam"


def DECONTAM(
    config: Config,
    sample_iterator: AutobfxIterator = None,
    host_iterator: AutobfxIterator = None,
) -> AutobfxFlow:
    input_reads = AutobfxFlow.gather_samples(
        config.flows["align_to_host"].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        sample_iterator,
    )
    extra_inputs = AutobfxFlow.gather_files(
        config.flows["build_host_index"].get_extra_inputs(config.project_fp)["hosts"][
            0
        ],
        "fasta",
        host_iterator,
    )
    sample_iterator = AutobfxIterator.gather(
        [{"sample": s} for s, _ in input_reads.items()], sample_iterator
    )
    host_iterator = AutobfxIterator.gather(
        [{"host": host_name} for host_name in extra_inputs.keys()],
        host_iterator,
    )

    flow = AutobfxFlow.compose_flows(
        NAME,
        [
            BUILD_HOST_INDEX(config, host_iterator=host_iterator),
            ALIGN_TO_HOST(
                config, sample_iterator=sample_iterator, host_iterator=host_iterator
            ),
            SORT_SAM(
                config, sample_iterator=sample_iterator, host_iterator=host_iterator
            ),
        ],
    )
    flow.connect_one_to_many(host_iterator, "build_host_index", "align_to_host")
    flow.connect_one_to_one(
        AutobfxIterator.expand([sample_iterator, host_iterator]),
        "align_to_host",
        "sort_sam",
    )

    return flow
