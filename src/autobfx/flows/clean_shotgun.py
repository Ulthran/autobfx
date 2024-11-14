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
        task.tag_str: task.submit() for task in TRIMMOMATIC(Config(**config)).tasks
    }
    heyfastq_submissions = {
        task.tag_str: task.submit(wait_for=[trimmomatic_submissions[task.tag_str]])
        for task in HEYFASTQ(Config(**config)).tasks
    }
    fastqc_submissions = {
        task.tag_str: task.submit(wait_for=[trimmomatic_submissions[task.tag_str]])
        for task in FASTQC(Config(**config)).tasks
    }

    build_host_index_submissions = {
        task.tag_str: task.submit() for task in BUILD_HOST_INDEX(Config(**config)).tasks
    }
    align_to_host_submissions = {
        task.tag_str: task.submit(
            wait_for=[
                heyfastq_submissions[task.tag_str],
                build_host_index_submissions[task.tag_str],
            ]
        )
        for task in ALIGN_TO_HOST(Config(**config)).tasks
    }  # TODO: Tagging so that this works...

    return [
        s.result()
        for s in list(fastqc_submissions.values())
        + list(align_to_host_submissions.values())
    ]

    qc_results = {sample_name: {} for sample_name in samples_list.keys()}
    for sample_name, r1 in samples_list.items():
        with tags(sample_name):
            with tags("trimmomatic"):
                qc_results[sample_name]["trimmomatic"] = run_trimmomatic.submit(
                    input_fp=r1,
                    output_fp=trimmomatic_output_fp / r1.name,
                    log_fp=trimmomatic_log_fp / f"{sample_name}.log",
                    env=config.flows["trimmomatic"].env,
                    paired_end=config.paired_end,
                    **config.flows["trimmomatic"].parameters,
                )

            with tags("heyfastq"):
                qc_results[sample_name]["heyfastq"] = run_heyfastq.submit(
                    input_fp=r1,
                    output_fp=heyfastq_output_fp / r1.name,
                    log_fp=heyfastq_log_fp / f"{sample_name}.log",
                    paired_end=config.paired_end,
                    **config.flows["heyfastq"].parameters,
                    wait_for=[qc_results[sample_name]["trimmomatic"]],
                )

            with tags("fastqc"):
                qc_results[sample_name]["fastqc"] = run_fastqc.submit(
                    input_fp=r1,
                    output_fp=fastqc_output_fp / r1.name,
                    log_fp=fastqc_log_fp / f"{sample_name}.log",
                    env=config.flows["fastqc"].env,
                    paired_end=config.paired_end,
                    **config.flows["fastqc"].parameters,
                    wait_for=[qc_results[sample_name]["trimmomatic"]],
                )

    build_host_index_results = {host_fp.stem: None for host_fp in hosts_list}
    for host_fp in hosts_list:
        with tags(host_fp.stem):
            with tags("build_host_index"):
                build_host_index_results[host_fp.stem] = run_build_host_index.submit(
                    input_fp=host_fp,
                    output_fp=build_host_index_output_fp / host_fp.name,
                    log_fp=build_host_index_log_fp / f"{host_fp.stem}.log",
                    env=config.flows["build_host_index"].env,
                    **config.flows["build_host_index"].parameters,
                )

    align_to_host_results = {
        (sample_name, host_fp.stem): None
        for sample_name in samples_list.keys()
        for host_fp in hosts_list
    }
    for sample_name, r1 in samples_list.items():
        with tags(sample_name):
            with tags("align_to_host"):
                for host_fp in hosts_list:
                    with tags(host_fp.stem):
                        align_to_host_results[(sample_name, host_fp.stem)] = (
                            run_align_to_host.submit(
                                input_fp=r1,
                                output_fp=align_to_host_output_fp
                                / f"{sample_name}.sam",
                                log_fp=align_to_host_log_fp / f"{sample_name}.log",
                                host_fp=host_fp,
                                env=config.flows["align_to_host"].env,
                                paired_end=config.paired_end,
                                **config.flows["align_to_host"].parameters,
                                wait_for=[
                                    qc_results[sample_name]["heyfastq"],
                                    build_host_index_results[host_fp.stem],
                                ],
                            )
                        )

    return qc_results, align_to_host_results
