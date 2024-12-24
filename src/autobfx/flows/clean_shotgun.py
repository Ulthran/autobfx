from pathlib import Path
from autobfx.flows.qc import QC
from autobfx.flows.decontam import DECONTAM
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.iterator import AutobfxIterator


NAME = "clean_shotgun"


def CLEAN_SHOTGUN(
    config: Config,
    sample_iterator: AutobfxIterator = None,
    host_iterator: AutobfxIterator = None,
) -> AutobfxFlow:
    input_reads = AutobfxFlow.gather_samples(
        config.flows["trimmomatic"].get_input_reads(config.project_fp)[0],
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
            QC(config, sample_iterator=sample_iterator),
            DECONTAM(
                config, sample_iterator=sample_iterator, host_iterator=host_iterator
            ),
        ],
    )
    flow.connect_one_to_many(sample_iterator, "heyfastq", "align_to_host")

    return flow
