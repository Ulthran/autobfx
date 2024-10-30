import argparse
from pathlib import Path
from prefect import flow
from flows.trimmomatic import trimmomatic_flow
from flows.fastqc import fastqc_flow
from tasks.lib.config import Config
from tasks.lib.utils import gather_samples


@flow(name="qc", log_prints=True)
def qc_flow(project_fp: Path, config: Config) -> list[Path]:
    trimmomatic_flow()
    # heyfastq()
    fastqc_flow()

    return "qc"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run QC")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args()
    config = Config(Path(args.project_fp).absolute() / "config.yaml")

    qc_flow(project_fp=Path(args.project_fp).absolute(), config=config)
