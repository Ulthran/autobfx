import os
from pathlib import Path
from prefect import task
from prefect_shell import ShellOperation
from autobfx.lib.utils import check_already_done, mark_as_done


@task
def run_heyfastq(
    input_fp: Path,
    output_fp: Path,
    log_fp: Path,
    paired_end: bool = True,
    sub_cmd: str = "filter-kscore",
    min_kscore: float = 0.5,
) -> Path:
    # Check files
    if check_already_done(output_fp):
        return output_fp
    if not input_fp.exists():
        raise FileNotFoundError(f"Input file not found: {input_fp}")
    if paired_end:
        input_pair_fp = Path(str(input_fp).replace("_R1", "_R2"))
        output_pair_fp = Path(str(output_fp).replace("_R1", "_R2"))

        if not input_pair_fp.exists():
            raise FileNotFoundError(f"Paired-end file not found: {input_pair_fp}")

    # TODO: Just use the python API instead of the shell command
    # Create command
    cmd = ["heyfastq", sub_cmd]
    cmd += ["--input", str(input_fp), str(input_pair_fp)] if paired_end else ["--input", str(input_fp)]
    cmd += ["--output", str(output_fp), str(output_pair_fp)] if paired_end else ["--output", str(output_fp)]
    cmd += ["--min-kscore", str(min_kscore)]

    # Run command
    shell_output = ShellOperation(
        commands=[
            " ".join(cmd),
        ]
    ).run()

    with open(log_fp, "w") as f:
        f.writelines(shell_output)

    mark_as_done(output_fp)

    return output_fp
