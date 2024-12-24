from autobfx.flows.fastqc import FASTQC
from autobfx.flows.heyfastq import HEYFASTQ
from autobfx.flows.trimmomatic import TRIMMOMATIC
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.io import IOReads
from autobfx.lib.iterator import AutobfxIterator


NAME = "qc"


def QC(config: Config, sample_iterator: AutobfxIterator = None) -> AutobfxFlow:
    input_reads = AutobfxFlow.gather_samples(
        config.flows["trimmomatic"].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        sample_iterator,
    )
    sample_iterator = AutobfxIterator.gather(
        [{"sample": s} for s, _ in input_reads.items()], sample_iterator
    )

    flow = AutobfxFlow.compose_flows(
        NAME,
        [
            TRIMMOMATIC(config, sample_iterator=sample_iterator),
            HEYFASTQ(config, sample_iterator=sample_iterator),
            FASTQC(config, sample_iterator=sample_iterator),
        ],
    )

    flow.connect_one_to_one(sample_iterator, "trimmomatic", "heyfastq")
    flow.connect_one_to_one(sample_iterator, "trimmomatic", "fastqc")

    return flow
