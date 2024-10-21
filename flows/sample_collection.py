from pathlib import Path
from prefect import flow
from tasks.lib.project import Project


@flow(name="sample_collection", log_prints=True)
def sample_collection_flow(
    project: Project = Project(Path(".")),
    files: list[Path] = [],
    directories: list[Path] = [],
    uris: list[str] = [],
):
    # Need to determine how we want to organize projects
    # Do we want each project to be a directory? Then it can house the collected samples
    # and the sample metadata (which can be as complicated or not as the project demands)

    print("HEY")


if __name__ == "__main__":
    # sample_collection_flow.visualize()
    sample_collection_flow.deploy(name="sample_collection", work_pool_name="default")
