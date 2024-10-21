from prefect import task


@task
def run_trimmomatic():
    print("Running Trimmomatic")
    return "trimmomatic"
