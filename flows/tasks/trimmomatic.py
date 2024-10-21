import os
import subprocess as sp
from pathlib import Path
from prefect import task


@task
def run_trimmomatic(
    input_fp: Path,
    output_fp: Path,
    log_fp: Path,
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
    if not input_fp.exists():
        raise FileNotFoundError(f"Input file not found: {input_fp}")
    if paired_end:
        input_pair_fp = Path(str(input_fp).replace("_R1", "_R2"))
        output_pair_fp = Path(str(output_fp).replace("_R1", "_R2"))
        output_unpair_1_fp = Path(str(output_fp).replace("_R1", "_unpair_R1"))
        output_unpair_2_fp = Path(str(output_fp).replace("_R1", "_unpair_R2"))
        if not input_pair_fp.exists():
            raise FileNotFoundError(f"Paired-end file not found: {input_pair_fp}")
    if not adapter_template:
        raise FileNotFoundError(f"Adapter template not found: {adapter_template}")

    # Create command
    cmd = ["conda", "activate", "trimmomatic", "&&", "trimmomatic"]
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
    with open(log_fp, "w") as f:
        # Consider using sp.Popen for finer control over running process
        sp.run(cmd, shell=True, executable="/bin/bash", stdout=f, stderr=f)

    return output_fp
