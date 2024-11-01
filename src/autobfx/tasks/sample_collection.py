from pathlib import Path
from prefect import task


ALLOWED_EXTENSIONS = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}


@task
def collect_samples_from_directory(dir: Path):
    print(f"Collecting samples from {dir}")
