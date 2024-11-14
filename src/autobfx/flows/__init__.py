from autobfx.flows.trimmomatic import trimmomatic_flow
from autobfx.flows.fastqc import fastqc_flow
from autobfx.flows.heyfastq import heyfastq_flow
from autobfx.flows.bwa import build_host_index_flow, align_to_host_flow
from autobfx.flows.qc import qc_flow
from autobfx.flows.decontam import decontam_flow
from autobfx.flows.clean_shotgun import clean_shotgun_flow
from pathlib import Path


root = Path(__file__).parent
flows = {
    "trimmomatic:trimmomatic_flow": trimmomatic_flow,
    "fastqc:fastqc_flow": fastqc_flow,
    "heyfastq:heyfastq_flow": heyfastq_flow,
    "bwa:build_host_index_flow": build_host_index_flow,
    "bwa:align_to_host_flow": align_to_host_flow,
    "qc:qc_flow": qc_flow,
    "decontam:decontam_flow": decontam_flow,
    "clean_shotgun:clean_shotgun_flow": clean_shotgun_flow,
}
