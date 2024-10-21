from prefect import task


@task
def run_fastqc():
    print("Running FastQC")
    return "fastqc"
