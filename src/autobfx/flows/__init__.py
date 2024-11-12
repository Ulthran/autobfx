from autobfx.flows.trimmomatic import trimmomatic_flow
from autobfx.flows.fastqc import fastqc_flow
from autobfx.flows.heyfastq import heyfastq_flow
from autobfx.flows.bwa import build_host_index_flow, align_to_host_flow

__dict__ = {
    "trimmomatic": trimmomatic_flow,
    "fastqc": fastqc_flow,
    "heyfastq": heyfastq_flow,
}
