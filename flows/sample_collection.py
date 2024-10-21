import argparse
from pathlib import Path
from prefect import flow
from tasks.sample_collection import collect_samples_from_directory
from tasks.lib.config import Config


@flow(name="sample_collection", log_prints=True)
def sample_collection_flow(
    project_fp: Path,
    files: list[Path] = [],
    directories: list[Path] = [],
    uris: list[str] = [],
):
    print(f"Collecting samples for project: {project_fp}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect samples for a project")
    parser.add_argument("project_fp", type=str, help="Filepath to the project")
    args = parser.parse_args()
    config = Config(Path(args.project_fp).absolute() / "config.yaml")
    print(config.get_flow("sample_collection"))

    sample_collection_flow(project_fp=Path(args.project_fp).absolute())
    # sample_collection_flow.visualize()
    # flow.from_source(
    #    source=str(Path(__file__).parent),
    #    entrypoint="sample_collection.py:sample_collection_flow",
    # ).deploy(
    #    name="sample_collection",
    #    work_pool_name="default",
    #    parameters=dict(
    #        project_fp=args.project_fp,
    #    ),
    # )
