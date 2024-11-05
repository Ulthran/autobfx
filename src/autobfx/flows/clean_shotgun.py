import argparse
from pathlib import Path
from prefect import flow, tags
from prefect.deployments import run_deployment
from prefect.states import Completed
from autobfx.flows.qc import qc_flow
from autobfx.flows.decontam import decontam_flow
from autobfx.tasks.bwa import run_build_host_index, run_align_to_host
from autobfx.tasks.fastqc import run_fastqc
from autobfx.tasks.heyfastq import run_heyfastq
from autobfx.tasks.trimmomatic import run_trimmomatic
from autobfx.lib.config import Config, config_from_yaml
from autobfx.lib.utils import (
    gather_samples,
    get_input_fp,
    setup_step,
)


NAME = "clean_shotgun"


@flow(name=NAME, log_prints=True)  # , task_runner=ThreadPoolTaskRunner(max_workers=5))
def clean_shotgun_flow(
    project_fp: Path, config: Config, samples: dict[str, Path] = {}
) -> list[Path]:
    # qc_results = qc_flow(project_fp, config, samples=samples)
    # decontam_flow(project_fp, config, samples=samples, input_dependencies={k: v["heyfastq"] for k, v in qc_results.items()})

    samples_list = (
        samples
        if samples
        else gather_samples(
            get_input_fp(Path(config.flows[NAME].input), project_fp),
            config.paired_end,
        )
    )
    hosts_list = [
        x.resolve()
        for x in Path(config.flows[NAME].parameters["hosts"]).glob("*.fasta")
    ]

    # Setup
    trimmomatic_input_fp, trimmomatic_output_fp, trimmomatic_log_fp = setup_step(
        project_fp, config, "trimmomatic"
    )
    heyfastq_input_fp, heyfastq_output_fp, heyfastq_log_fp = setup_step(
        project_fp, config, "heyfastq"
    )
    fastqc_input_fp, fastqc_output_fp, fastqc_log_fp = setup_step(
        project_fp, config, "fastqc"
    )
    build_host_index_input_fp, build_host_index_output_fp, build_host_index_log_fp = (
        setup_step(project_fp, config, "build_host_index")
    )
    align_to_host_input_fp, align_to_host_output_fp, align_to_host_log_fp = setup_step(
        project_fp, config, "align_to_host"
    )
    (
        filter_host_reads_input_fp,
        filter_host_reads_output_fp,
        filter_host_reads_log_fp,
    ) = setup_step(project_fp, config, "filter_host_reads")
    (
        preprocess_report_input_fp,
        preprocess_report_output_fp,
        preprocess_report_log_fp,
    ) = setup_step(project_fp, config, "preprocess_report")

    # Preprocess

    # Run
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run {NAME}")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    parser.add_argument(
        "--samples",
        nargs="*",
        default=[],
        help="Specific samples to run (provide full sample names e.g. 'sample1_R1.fastq.gz' as they appear in the input directory for this flow)",
    )
    args = parser.parse_args()
    config = config_from_yaml(Path(args.project_fp).absolute() / "config.yaml")

    samples = gather_samples(Path(config.flows[NAME].input), config.paired_end)
    if args.samples:
        samples = {k: v for k, v in samples.items() if Path(v).name in args.samples}
        if missing := [x for x in args.samples if x not in samples.keys()]:
            raise FileNotFoundError(f"Samples not found: {missing}")

    decontam_flow.from_source(
        source=str(Path(__file__).parent),
        entrypoint="clean_shotgun.py:clean_shotgun_flow",
    ).deploy(
        name=f"{NAME}_deployment",
        work_pool_name="default",
        ignore_warnings=True,
    )

    run_deployment(
        f"{NAME}/{NAME}_deployment",
        parameters={
            "project_fp": Path(args.project_fp).absolute(),
            "config": config,
            "samples": samples,
        },
    )