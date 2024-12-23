from autobfx.flows.fastqc import FASTQC
from autobfx.flows.heyfastq import HEYFASTQ
from autobfx.flows.trimmomatic import TRIMMOMATIC
from autobfx.lib.config import Config
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.iterator import AutobfxIterator, SampleIterator


NAME = "qc"


def QC(config: Config, samples: SampleIterator = None) -> AutobfxFlow:
    sample_iterator = SampleIterator.gather_samples(
        config.flows["trimmomatic"].get_input_reads(config.project_fp)[0],
        config.paired_end,
        config.samples,
        samples,
    )

    flow = AutobfxFlow.compose_flows(
        NAME,
        [
            TRIMMOMATIC(config, samples=sample_iterator),
            HEYFASTQ(config, samples=sample_iterator),
            FASTQC(config, samples=sample_iterator),
        ],
    )

    flow.connect_one_to_one(sample_iterator, "trimmomatic", "heyfastq")
    flow.connect_one_to_one(sample_iterator, "trimmomatic", "fastqc")

    return flow
