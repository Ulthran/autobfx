import os
from pathlib import Path
from prefect_shell import ShellOperation
from autobfx.lib.io import IOObject, IOReads


def run_trimmomatic(
    input_reads: list[IOReads],
    extra_inputs: dict[str, list[IOObject]],
    output_reads: list[IOReads],
    extra_outputs: dict[str, list[IOObject]],
    # runner
    log_fp: Path,
    threads: int = 1,
    leading: int = 3,
    trailing: int = 3,
    sw_start: int = 4,
    sw_end: int = 15,
    minlen: int = 36,
):
    try:
        adapter_template = extra_inputs["adapter_template"][0].fp
    except KeyError:
        adapter_template = None

    cmd = ["trimmomatic"]
    cmd += ["PE"] if not input_reads[0].r2 else ["SE"]
    cmd += ["-threads", str(threads)]
    cmd += ["-phred33"]
    cmd += (
        [str(input_reads[0].fp), str(input_reads[0].r2)]
        if input_reads[0].r2
        else [str(input_reads[0].fp)]
    )
    cmd += (
        [
            str(output_reads[0].fp),
            str(output_reads[1].fp),
            str(output_reads[0].r2),
            str(output_reads[1].r2),
        ]
        if input_reads[0].r2
        else [str(output_reads[0].fp)]
    )
    cmd += ["ILLUMINACLIP:" + str(adapter_template) + ":2:30:10:8:true"]
    cmd += ["LEADING:" + str(leading)]
    cmd += ["TRAILING:" + str(trailing)]
    cmd += ["SLIDINGWINDOW:" + str(sw_start) + ":" + str(sw_end)]
    cmd += ["MINLEN:" + str(minlen)]

    print(f"Running {' '.join(cmd)}")

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
