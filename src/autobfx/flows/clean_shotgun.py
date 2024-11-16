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
from autobfx.lib.flow import AutobfxFlow
from autobfx.lib.utils import (
    gather_samples,
    get_input_fp,
    setup_step,
)


def CLEAN_SHOTGUN(config: Config) -> AutobfxFlow:
    NAME = "clean_shotgun"
    project_fp = config.project_fp
    hosts_list = {
        x.stem: x.resolve()
        for x in Path(
            config.flows["build_host_index"].get_extra_inputs(project_fp)["hosts"][0]
        ).glob("*.fasta")
    }
    samples_list = gather_samples(
        config.flows["trimmomatic"].get_input_reads(project_fp)[0],
        config.paired_end,
        config.samples,
    )

    trimmomatic_submissions = {
        task.ids: task.submit()
        for task in TRIMMOMATIC(config, samples=samples_list).tasks
    }
    heyfastq_submissions = {
        task.ids: task.submit(wait_for=[trimmomatic_submissions[task.ids]])
        for task in HEYFASTQ(config, samples=samples_list).tasks
    }
    fastqc_submissions = {
        task.ids: task.submit(wait_for=[trimmomatic_submissions[task.ids]])
        for task in FASTQC(config, samples=samples_list).tasks
    }

    build_host_index_submissions = {
        task.ids: task.submit()
        for task in BUILD_HOST_INDEX(config, hosts=hosts_list).tasks
    }
    align_to_host_submissions = {
        task.ids: task.submit(
            wait_for=[
                heyfastq_submissions[tuple([task.ids[0]])],
                build_host_index_submissions[tuple([task.ids[1]])],
            ]
        )
        for task in ALIGN_TO_HOST(config, samples=samples_list, hosts=hosts_list).tasks
    }

    # Combine on sample_name by waiting for {k: v for k, v in align_to_host_submissions if sample_name in k}

    return AutobfxFlow(
        config,
        NAME,
        [
            *trimmomatic_submissions.values(),
            *heyfastq_submissions.values(),
            *fastqc_submissions.values(),
            *build_host_index_submissions.values(),
            *align_to_host_submissions.values(),
        ],
    )


@flow(name="clean_shotgun", log_prints=True)
def clean_shotgun_flow(config: dict) -> list[Path]:
    # TODO: Fix this, should be submitting here not in CLEAN_SHOTGUN
    # Need to pass wait_for to here somehow, adjust AutobfxFlow to accept
    submissions = [t for t in CLEAN_SHOTGUN(Config(**config)).tasks]
    return [s.result() for s in submissions]
