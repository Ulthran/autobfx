import os
from pathlib import Path
from prefect import task
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.utils import check_already_done, mark_as_done


def run_trimmomatic(
    input_reads: list[IOReads],
    extra_inputs: dict[str, IOObject],
    output_reads: list[IOReads],
    extra_outputs: dict[str, IOObject],
    log_fp: Path,
    threads: int = 1,
    adapter_template: Path = None,
    leading: int = 3,
    trailing: int = 3,
    sw_start: int = 4,
    sw_end: int = 15,
    minlen: int = 36,
):
    r1_in = input_reads[0].fp
    r2_in = input_reads[0].r2
    paired_end = r2_in is not None
    r1_out = output_reads[0].fp
    r2_out = output_reads[0].r2
    try:
        r1_unpair = output_reads[1].fp
        r2_unpair = output_reads[1].r2
    except IndexError:
        r1_unpair = None
        r2_unpair = None

    cmd = ["trimmomatic"]
    cmd += ["PE"] if paired_end else ["SE"]
    cmd += ["-threads", str(threads)]
    cmd += ["-phred33"]
    cmd += [str(r1_in), str(r2_in)] if paired_end else [str(r1_in)]
    cmd += (
        [
            str(r1_out),
            str(r1_unpair),
            str(r2_out),
            str(r2_unpair),
        ]
        if paired_end
        else [str(r1_out)]
    )
    cmd += ["ILLUMINACLIP:" + str(adapter_template) + ":2:30:10:8:true"]
    cmd += ["LEADING:" + str(leading)]
    cmd += ["TRAILING:" + str(trailing)]
    cmd += ["SLIDINGWINDOW:" + str(sw_start) + ":" + str(sw_end)]
    cmd += ["MINLEN:" + str(minlen)]

    print(f"Running {' '.join(cmd)}")

    # Run command
    with ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"conda activate trimmomatic",
            " ".join(cmd),
        ],
        stream_output=False,
    ) as shell_operation:
        shell_process = shell_operation.trigger()
        shell_process.wait_for_completion()
        shell_output = shell_process.fetch_result()

    with open(log_fp, "w") as f:
        f.writelines(shell_output)

    return 1


@task
def OLDrun_trimmomatic(
    input_fp: Path,
    output_fp: Path,
    log_fp: Path,
    conda_env: str,
    paired_end: bool = True,
    threads: int = 1,
    adapter_template: Path = None,
    leading: int = 3,
    trailing: int = 3,
    sw_start: int = 4,
    sw_end: int = 15,
    minlen: int = 36,
) -> Path:
    # Check files
    if check_already_done(output_fp):
        return output_fp
    if not input_fp.exists():
        raise FileNotFoundError(f"Input file not found: {input_fp}")
    if paired_end:
        input_pair_fp = Path(str(input_fp).replace("_R1", "_R2"))
        output_pair_fp = Path(str(output_fp).replace("_R1", "_R2"))

        extra_output_fp = output_fp.parent / "extra"
        extra_output_fp.mkdir(exist_ok=True)
        output_unpair_1_fp = extra_output_fp / str(output_fp.name).replace(
            "_R1", "_unpair_R1"
        )
        output_unpair_2_fp = extra_output_fp / str(output_pair_fp.name).replace(
            "_R2", "_unpair_R2"
        )
        if not input_pair_fp.exists():
            raise FileNotFoundError(f"Paired-end file not found: {input_pair_fp}")
    if not adapter_template:
        adapter_template = (
            Path(os.environ.get("CONDA_PREFIX", ""))
            / "envs"
            / conda_env
            / "share/trimmomatic/adapters/NexteraPE-PE.fa"
        )
    if not adapter_template.exists():
        raise FileNotFoundError(f"Adapter template not found: {adapter_template}")

    # Create command
    cmd = ["trimmomatic"]
    cmd += ["PE"] if paired_end else ["SE"]
    cmd += ["-threads", str(threads)]
    cmd += ["-phred33"]
    cmd += [str(input_fp), str(input_pair_fp)] if paired_end else [str(input_fp)]
    cmd += (
        [
            str(output_fp),
            str(output_unpair_1_fp),
            str(output_pair_fp),
            str(output_unpair_2_fp),
        ]
        if paired_end
        else [str(output_fp)]
    )
    cmd += ["ILLUMINACLIP:" + str(adapter_template) + ":2:30:10:8:true"]
    cmd += ["LEADING:" + str(leading)]
    cmd += ["TRAILING:" + str(trailing)]
    cmd += ["SLIDINGWINDOW:" + str(sw_start) + ":" + str(sw_end)]
    cmd += ["MINLEN:" + str(minlen)]

    # Run command
    with ShellOperation(
        commands=[
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"conda activate {conda_env}",
            " ".join(cmd),
        ],
        stream_output=False,
    ) as shell_operation:
        shell_process = shell_operation.trigger()
        shell_process.wait_for_completion()
        shell_output = shell_process.fetch_result()

    with open(log_fp, "w") as f:
        f.writelines(shell_output)

    mark_as_done(output_fp)

    return output_fp
