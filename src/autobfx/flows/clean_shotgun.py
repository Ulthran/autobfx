import argparse
from pathlib import Path
from prefect import flow, tags
from prefect.deployments import run_deployment
from prefect.states import Completed
from autobfx.flows.qc import qc_flow
from autobfx.flows.decontam import decontam_flow
from autobfx.flows.trimmomatic import TRIMMOMATIC
from autobfx.flows.bwa import BUILD_HOST_INDEX, ALIGN_TO_HOST
from autobfx.flows.fastqc import FASTQC
from autobfx.flows.heyfastq import HEYFASTQ
from autobfx.lib.config import Config
from autobfx.lib.utils import (
    gather_samples,
    get_input_fp,
    setup_step,
)


NAME = "clean_shotgun"


@flow(name=NAME, log_prints=True)
def clean_shotgun_flow(config: dict) -> list[Path]:
    trimmomatic_submissions = {
        task.ids: task.submit() for task in TRIMMOMATIC(Config(**config)).tasks
    }
    heyfastq_submissions = {
        task.ids: task.submit(wait_for=[trimmomatic_submissions[task.ids]])
        for task in HEYFASTQ(Config(**config)).tasks
    }
    fastqc_submissions = {
        task.ids: task.submit(wait_for=[trimmomatic_submissions[task.ids]])
        for task in FASTQC(Config(**config)).tasks
    }

    build_host_index_submissions = {
        task.ids: task.submit() for task in BUILD_HOST_INDEX(Config(**config)).tasks
    }
    align_to_host_submissions = {
        task.ids: task.submit(
            wait_for=[
                heyfastq_submissions[task.ids[0]],
                build_host_index_submissions[task.ids[1]],
            ]
        )
        for task in ALIGN_TO_HOST(Config(**config)).tasks
    }

    # Combine on sample_name by waiting for {k: v for k, v in align_to_host_submissions if sample_name in k}

    return [
        s.result()
        for s in list(fastqc_submissions.values())
        + list(align_to_host_submissions.values())
    ]
