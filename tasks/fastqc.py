from prefect import task


@task
def fastqc():
    print("Running FastQC")
    return "fastqc"
